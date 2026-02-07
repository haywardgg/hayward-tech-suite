"""
System performance profiler for Ghosty Toolz Evolved.

Provides detailed system performance analysis including CPU, memory,
disk, and process profiling with trend analysis and recommendations.
"""

import psutil
import time
import statistics
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger("performance_profiler")


class PerformanceLevel(Enum):
    """System performance levels."""
    
    OPTIMAL = "optimal"
    GOOD = "good"
    MODERATE = "moderate"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass
class CPUProfile:
    """CPU performance profile."""
    
    current_usage: float
    average_usage: float
    per_core_usage: List[float]
    frequency_current: float
    frequency_max: float
    core_count: int
    thread_count: int
    temperature: Optional[float] = None


@dataclass
class MemoryProfile:
    """Memory performance profile."""
    
    total: int
    available: int
    used: int
    percent_used: float
    swap_total: int
    swap_used: int
    swap_percent: float


@dataclass
class DiskProfile:
    """Disk performance profile."""
    
    device: str
    total: int
    used: int
    free: int
    percent_used: float
    read_count: int
    write_count: int
    read_bytes: int
    write_bytes: int
    read_time: int
    write_time: int


@dataclass
class ProcessInfo:
    """Process information."""
    
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    num_threads: int
    status: str
    username: str


class PerformanceProfilerError(Exception):
    """Custom exception for performance profiler errors."""
    
    pass


class PerformanceProfiler:
    """System performance profiling and analysis."""
    
    def __init__(self, sample_interval: float = 0.5) -> None:
        """
        Initialize performance profiler.
        
        Args:
            sample_interval: Interval between samples in seconds
        """
        self.sample_interval = sample_interval
        logger.info("Performance profiler initialized")
    
    def profile_cpu(self, duration: int = 5) -> CPUProfile:
        """
        Profile CPU performance over specified duration.
        
        Args:
            duration: Profiling duration in seconds
        
        Returns:
            CPU performance profile
        """
        logger.info(f"Profiling CPU for {duration} seconds")
        
        # Collect samples
        samples = []
        sample_count = int(duration / self.sample_interval)
        
        for _ in range(sample_count):
            samples.append(psutil.cpu_percent(interval=self.sample_interval))
        
        # Get detailed CPU info
        cpu_freq = psutil.cpu_freq()
        per_core = psutil.cpu_percent(percpu=True)
        
        profile = CPUProfile(
            current_usage=samples[-1],
            average_usage=statistics.mean(samples),
            per_core_usage=per_core,
            frequency_current=cpu_freq.current if cpu_freq else 0,
            frequency_max=cpu_freq.max if cpu_freq else 0,
            core_count=psutil.cpu_count(logical=False) or 0,
            thread_count=psutil.cpu_count(logical=True) or 0
        )
        
        logger.info(
            f"CPU profile: Avg usage {profile.average_usage:.1f}%, "
            f"{profile.core_count} cores, {profile.thread_count} threads"
        )
        
        return profile
    
    def profile_memory(self) -> MemoryProfile:
        """
        Profile memory usage.
        
        Returns:
            Memory performance profile
        """
        logger.info("Profiling memory")
        
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        profile = MemoryProfile(
            total=vm.total,
            available=vm.available,
            used=vm.used,
            percent_used=vm.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_percent=swap.percent
        )
        
        logger.info(
            f"Memory profile: {profile.percent_used:.1f}% used "
            f"({profile.used / (1024**3):.1f}GB / {profile.total / (1024**3):.1f}GB)"
        )
        
        return profile
    
    def profile_disk(self, path: str = 'C:\\') -> DiskProfile:
        """
        Profile disk performance.
        
        Args:
            path: Disk path to profile
        
        Returns:
            Disk performance profile
        """
        logger.info(f"Profiling disk: {path}")
        
        # Get disk usage
        usage = psutil.disk_usage(path)
        
        # Get disk I/O stats (system-wide on Windows)
        io_counters = psutil.disk_io_counters()
        
        profile = DiskProfile(
            device=path,
            total=usage.total,
            used=usage.used,
            free=usage.free,
            percent_used=usage.percent,
            read_count=io_counters.read_count if io_counters else 0,
            write_count=io_counters.write_count if io_counters else 0,
            read_bytes=io_counters.read_bytes if io_counters else 0,
            write_bytes=io_counters.write_bytes if io_counters else 0,
            read_time=io_counters.read_time if io_counters else 0,
            write_time=io_counters.write_time if io_counters else 0
        )
        
        logger.info(
            f"Disk profile: {profile.percent_used:.1f}% used "
            f"({profile.used / (1024**3):.1f}GB / {profile.total / (1024**3):.1f}GB)"
        )
        
        return profile
    
    def get_top_processes(
        self,
        sort_by: str = 'cpu',
        limit: int = 10
    ) -> List[ProcessInfo]:
        """
        Get top processes by CPU or memory usage.
        
        Args:
            sort_by: Sort by 'cpu' or 'memory'
            limit: Maximum number of processes to return
        
        Returns:
            List of top processes
        """
        logger.info(f"Getting top {limit} processes by {sort_by}")
        
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'num_threads']):
            try:
                # Get process info
                pinfo = proc.info
                cpu_percent = proc.cpu_percent(interval=0.1)
                mem_info = proc.memory_info()
                mem_percent = proc.memory_percent()
                
                process_info = ProcessInfo(
                    pid=pinfo['pid'],
                    name=pinfo['name'],
                    cpu_percent=cpu_percent,
                    memory_percent=mem_percent,
                    memory_mb=mem_info.rss / (1024 * 1024),
                    num_threads=pinfo['num_threads'],
                    status=pinfo['status'],
                    username=pinfo['username'] or 'N/A'
                )
                
                processes.append(process_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort processes
        if sort_by == 'cpu':
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        else:
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        
        top_processes = processes[:limit]
        
        logger.info(f"Found {len(processes)} processes, returning top {len(top_processes)}")
        
        return top_processes
    
    def assess_performance(self) -> PerformanceLevel:
        """
        Assess overall system performance.
        
        Returns:
            Performance level assessment
        """
        logger.info("Assessing system performance")
        
        # Get quick metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        # Critical conditions
        if cpu_percent > 95 or memory_percent > 95:
            return PerformanceLevel.CRITICAL
        
        # Degraded conditions
        if cpu_percent > 85 or memory_percent > 85:
            return PerformanceLevel.DEGRADED
        
        # Moderate conditions
        if cpu_percent > 70 or memory_percent > 70:
            return PerformanceLevel.MODERATE
        
        # Good conditions
        if cpu_percent > 50 or memory_percent > 50:
            return PerformanceLevel.GOOD
        
        # Optimal conditions
        return PerformanceLevel.OPTIMAL
    
    def get_system_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Identify system performance bottlenecks.
        
        Returns:
            List of identified bottlenecks with recommendations
        """
        logger.info("Analyzing system bottlenecks")
        
        bottlenecks = []
        
        # Check CPU
        cpu_profile = self.profile_cpu(duration=3)
        if cpu_profile.average_usage > 80:
            bottlenecks.append({
                'component': 'CPU',
                'severity': 'high' if cpu_profile.average_usage > 90 else 'medium',
                'description': f'CPU usage is high at {cpu_profile.average_usage:.1f}%',
                'recommendation': 'Close unnecessary applications or upgrade CPU',
                'value': cpu_profile.average_usage
            })
        
        # Check Memory
        mem_profile = self.profile_memory()
        if mem_profile.percent_used > 80:
            bottlenecks.append({
                'component': 'Memory',
                'severity': 'high' if mem_profile.percent_used > 90 else 'medium',
                'description': f'Memory usage is high at {mem_profile.percent_used:.1f}%',
                'recommendation': 'Close memory-intensive applications or add more RAM',
                'value': mem_profile.percent_used
            })
        
        # Check Disk
        disk_profile = self.profile_disk()
        if disk_profile.percent_used > 85:
            bottlenecks.append({
                'component': 'Disk Space',
                'severity': 'high' if disk_profile.percent_used > 95 else 'medium',
                'description': f'Disk usage is high at {disk_profile.percent_used:.1f}%',
                'recommendation': 'Free up disk space or add more storage',
                'value': disk_profile.percent_used
            })
        
        # Check for high I/O wait
        io_counters_before = psutil.disk_io_counters()
        time.sleep(1)
        io_counters_after = psutil.disk_io_counters()
        
        if io_counters_before and io_counters_after:
            read_time_diff = io_counters_after.read_time - io_counters_before.read_time
            write_time_diff = io_counters_after.write_time - io_counters_before.write_time
            total_io_time = read_time_diff + write_time_diff
            
            if total_io_time > 500:  # More than 500ms in I/O
                bottlenecks.append({
                    'component': 'Disk I/O',
                    'severity': 'medium',
                    'description': 'High disk I/O activity detected',
                    'recommendation': 'Consider upgrading to SSD or optimizing disk-intensive applications',
                    'value': total_io_time
                })
        
        logger.info(f"Found {len(bottlenecks)} bottlenecks")
        return bottlenecks
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Dictionary with performance assessment
        """
        logger.info("Generating performance report")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_performance': None,
            'cpu': {},
            'memory': {},
            'disk': {},
            'top_processes_cpu': [],
            'top_processes_memory': [],
            'bottlenecks': []
        }
        
        # Overall assessment
        try:
            report['overall_performance'] = self.assess_performance().value
        except Exception as e:
            logger.error(f"Performance assessment failed: {e}")
        
        # CPU profile
        try:
            cpu = self.profile_cpu(duration=3)
            report['cpu'] = {
                'average_usage': cpu.average_usage,
                'current_usage': cpu.current_usage,
                'core_count': cpu.core_count,
                'thread_count': cpu.thread_count,
                'frequency_current': cpu.frequency_current,
                'frequency_max': cpu.frequency_max
            }
        except Exception as e:
            logger.error(f"CPU profiling failed: {e}")
            report['cpu'] = {'error': str(e)}
        
        # Memory profile
        try:
            memory = self.profile_memory()
            report['memory'] = {
                'percent_used': memory.percent_used,
                'total_gb': memory.total / (1024**3),
                'used_gb': memory.used / (1024**3),
                'available_gb': memory.available / (1024**3),
                'swap_percent': memory.swap_percent
            }
        except Exception as e:
            logger.error(f"Memory profiling failed: {e}")
            report['memory'] = {'error': str(e)}
        
        # Disk profile
        try:
            disk = self.profile_disk()
            report['disk'] = {
                'percent_used': disk.percent_used,
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3)
            }
        except Exception as e:
            logger.error(f"Disk profiling failed: {e}")
            report['disk'] = {'error': str(e)}
        
        # Top processes
        try:
            top_cpu = self.get_top_processes(sort_by='cpu', limit=5)
            report['top_processes_cpu'] = [
                {
                    'name': p.name,
                    'pid': p.pid,
                    'cpu_percent': p.cpu_percent,
                    'memory_mb': p.memory_mb
                }
                for p in top_cpu
            ]
        except Exception as e:
            logger.error(f"Top CPU processes failed: {e}")
        
        try:
            top_mem = self.get_top_processes(sort_by='memory', limit=5)
            report['top_processes_memory'] = [
                {
                    'name': p.name,
                    'pid': p.pid,
                    'cpu_percent': p.cpu_percent,
                    'memory_mb': p.memory_mb
                }
                for p in top_mem
            ]
        except Exception as e:
            logger.error(f"Top memory processes failed: {e}")
        
        # Bottlenecks
        try:
            report['bottlenecks'] = self.get_system_bottlenecks()
        except Exception as e:
            logger.error(f"Bottleneck analysis failed: {e}")
            report['bottlenecks'] = {'error': str(e)}
        
        logger.info("Performance report generated")
        return report


# Example usage
if __name__ == "__main__":
    profiler = PerformanceProfiler()
    
    # Generate full report
    print("=== Performance Report ===")
    report = profiler.generate_performance_report()
    
    print(f"\nTimestamp: {report['timestamp']}")
    print(f"Overall Performance: {report['overall_performance']}")
    
    if 'cpu' in report and 'average_usage' in report['cpu']:
        print(f"\nCPU: {report['cpu']['average_usage']:.1f}% average")
        print(f"  Cores: {report['cpu']['core_count']}, Threads: {report['cpu']['thread_count']}")
    
    if 'memory' in report and 'percent_used' in report['memory']:
        print(f"\nMemory: {report['memory']['percent_used']:.1f}% used")
        print(f"  {report['memory']['used_gb']:.1f}GB / {report['memory']['total_gb']:.1f}GB")
    
    if 'disk' in report and 'percent_used' in report['disk']:
        print(f"\nDisk: {report['disk']['percent_used']:.1f}% used")
        print(f"  {report['disk']['used_gb']:.1f}GB / {report['disk']['total_gb']:.1f}GB")
    
    print(f"\nBottlenecks: {len(report.get('bottlenecks', []))}")
    for bottleneck in report.get('bottlenecks', []):
        if isinstance(bottleneck, dict):
            print(f"  [{bottleneck['severity'].upper()}] {bottleneck['component']}: {bottleneck['description']}")
