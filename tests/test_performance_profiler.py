"""Tests for performance profiler module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.performance_profiler import (
    PerformanceProfiler,
    PerformanceLevel,
    CPUProfile,
    MemoryProfile,
    DiskProfile,
    ProcessInfo
)


class TestPerformanceProfiler:
    """Test suite for PerformanceProfiler class."""
    
    @pytest.fixture
    def profiler(self):
        """Create PerformanceProfiler instance for testing."""
        return PerformanceProfiler(sample_interval=0.1)
    
    def test_initialization(self, profiler):
        """Test performance profiler initialization."""
        assert profiler is not None
        assert profiler.sample_interval == 0.1
    
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_freq')
    @patch('psutil.cpu_count')
    def test_profile_cpu(self, mock_cpu_count, mock_cpu_freq, mock_cpu_percent, profiler):
        """Test CPU profiling."""
        # Mock CPU data - need enough values for all samples
        mock_cpu_percent.return_value = 47.5  # Return same value for all calls
        mock_cpu_freq.return_value = MagicMock(current=2400, max=3600)
        mock_cpu_count.side_effect = [4, 8]  # physical, logical
        
        profiler.sample_interval = 0.01  # Speed up test
        profile = profiler.profile_cpu(duration=1)
        
        assert isinstance(profile, CPUProfile)
        assert profile.current_usage >= 0
        assert profile.average_usage >= 0
        assert profile.core_count >= 0
        assert profile.thread_count >= 0
    
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    def test_profile_memory(self, mock_swap, mock_vm, profiler):
        """Test memory profiling."""
        # Mock memory data
        mock_vm.return_value = MagicMock(
            total=16 * 1024**3,  # 16GB
            available=8 * 1024**3,  # 8GB
            used=8 * 1024**3,  # 8GB
            percent=50.0
        )
        mock_swap.return_value = MagicMock(
            total=4 * 1024**3,  # 4GB
            used=1 * 1024**3,  # 1GB
            percent=25.0
        )
        
        profile = profiler.profile_memory()
        
        assert isinstance(profile, MemoryProfile)
        assert profile.total > 0
        assert profile.percent_used >= 0
        assert profile.swap_percent >= 0
    
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    def test_profile_disk(self, mock_io, mock_usage, profiler):
        """Test disk profiling."""
        # Mock disk data
        mock_usage.return_value = MagicMock(
            total=500 * 1024**3,  # 500GB
            used=250 * 1024**3,  # 250GB
            free=250 * 1024**3,  # 250GB
            percent=50.0
        )
        mock_io.return_value = MagicMock(
            read_count=1000,
            write_count=500,
            read_bytes=1024**3,
            write_bytes=512**3,
            read_time=100,
            write_time=50
        )
        
        profile = profiler.profile_disk('C:\\')
        
        assert isinstance(profile, DiskProfile)
        assert profile.device == 'C:\\'
        assert profile.total > 0
        assert profile.percent_used >= 0
    
    @patch('psutil.process_iter')
    def test_get_top_processes(self, mock_process_iter, profiler):
        """Test getting top processes."""
        # Create mock processes
        mock_proc1 = MagicMock()
        mock_proc1.info = {
            'pid': 1234,
            'name': 'test_process.exe',
            'username': 'user',
            'status': 'running',
            'num_threads': 4
        }
        mock_proc1.cpu_percent.return_value = 25.0
        mock_proc1.memory_percent.return_value = 10.0
        mock_proc1.memory_info.return_value = MagicMock(rss=100 * 1024 * 1024)  # 100MB
        
        mock_proc2 = MagicMock()
        mock_proc2.info = {
            'pid': 5678,
            'name': 'another_process.exe',
            'username': 'user',
            'status': 'running',
            'num_threads': 2
        }
        mock_proc2.cpu_percent.return_value = 15.0
        mock_proc2.memory_percent.return_value = 5.0
        mock_proc2.memory_info.return_value = MagicMock(rss=50 * 1024 * 1024)  # 50MB
        
        mock_process_iter.return_value = [mock_proc1, mock_proc2]
        
        processes = profiler.get_top_processes(sort_by='cpu', limit=10)
        
        assert isinstance(processes, list)
        assert len(processes) > 0
        for proc in processes:
            assert isinstance(proc, ProcessInfo)
            assert proc.pid > 0
            assert proc.name
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_assess_performance_optimal(self, mock_memory, mock_cpu, profiler):
        """Test performance assessment - optimal."""
        mock_cpu.return_value = 30.0
        mock_memory.return_value = MagicMock(percent=40.0)
        
        level = profiler.assess_performance()
        
        assert level == PerformanceLevel.OPTIMAL
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_assess_performance_critical(self, mock_memory, mock_cpu, profiler):
        """Test performance assessment - critical."""
        mock_cpu.return_value = 98.0
        mock_memory.return_value = MagicMock(percent=97.0)
        
        level = profiler.assess_performance()
        
        assert level == PerformanceLevel.CRITICAL
    
    @patch.object(PerformanceProfiler, 'profile_cpu')
    @patch.object(PerformanceProfiler, 'profile_memory')
    @patch.object(PerformanceProfiler, 'profile_disk')
    def test_get_system_bottlenecks(self, mock_disk, mock_memory, mock_cpu, profiler):
        """Test bottleneck detection."""
        # Mock high CPU usage
        mock_cpu.return_value = CPUProfile(
            current_usage=95.0,
            average_usage=92.0,
            per_core_usage=[90.0, 94.0, 92.0, 91.0],
            frequency_current=2400,
            frequency_max=3600,
            core_count=4,
            thread_count=8
        )
        
        # Mock high memory usage
        mock_memory.return_value = MemoryProfile(
            total=16 * 1024**3,
            available=1 * 1024**3,
            used=15 * 1024**3,
            percent_used=94.0,
            swap_total=4 * 1024**3,
            swap_used=2 * 1024**3,
            swap_percent=50.0
        )
        
        # Mock normal disk usage
        mock_disk.return_value = DiskProfile(
            device='C:\\',
            total=500 * 1024**3,
            used=250 * 1024**3,
            free=250 * 1024**3,
            percent_used=50.0,
            read_count=1000,
            write_count=500,
            read_bytes=1024**3,
            write_bytes=512**3,
            read_time=100,
            write_time=50
        )
        
        bottlenecks = profiler.get_system_bottlenecks()
        
        assert isinstance(bottlenecks, list)
        # Should detect CPU and Memory bottlenecks
        assert len(bottlenecks) >= 2
        
        # Check that bottlenecks have required fields
        for bottleneck in bottlenecks:
            assert 'component' in bottleneck
            assert 'severity' in bottleneck
            assert 'description' in bottleneck
            assert 'recommendation' in bottleneck
    
    @patch.object(PerformanceProfiler, 'assess_performance')
    @patch.object(PerformanceProfiler, 'profile_cpu')
    @patch.object(PerformanceProfiler, 'profile_memory')
    @patch.object(PerformanceProfiler, 'profile_disk')
    @patch.object(PerformanceProfiler, 'get_top_processes')
    @patch.object(PerformanceProfiler, 'get_system_bottlenecks')
    def test_generate_performance_report(
        self,
        mock_bottlenecks,
        mock_top_processes,
        mock_disk,
        mock_memory,
        mock_cpu,
        mock_assess,
        profiler
    ):
        """Test performance report generation."""
        # Mock all the methods
        mock_assess.return_value = PerformanceLevel.GOOD
        
        mock_cpu.return_value = CPUProfile(
            current_usage=45.0,
            average_usage=50.0,
            per_core_usage=[48.0, 52.0],
            frequency_current=2400,
            frequency_max=3600,
            core_count=2,
            thread_count=4
        )
        
        mock_memory.return_value = MemoryProfile(
            total=8 * 1024**3,
            available=4 * 1024**3,
            used=4 * 1024**3,
            percent_used=50.0,
            swap_total=2 * 1024**3,
            swap_used=0,
            swap_percent=0.0
        )
        
        mock_disk.return_value = DiskProfile(
            device='C:\\',
            total=500 * 1024**3,
            used=250 * 1024**3,
            free=250 * 1024**3,
            percent_used=50.0,
            read_count=1000,
            write_count=500,
            read_bytes=1024**3,
            write_bytes=512**3,
            read_time=100,
            write_time=50
        )
        
        mock_top_processes.return_value = [
            ProcessInfo(
                pid=1234,
                name='test.exe',
                cpu_percent=10.0,
                memory_percent=5.0,
                memory_mb=100.0,
                num_threads=4,
                status='running',
                username='user'
            )
        ]
        
        mock_bottlenecks.return_value = []
        
        report = profiler.generate_performance_report()
        
        assert 'timestamp' in report
        assert 'overall_performance' in report
        assert report['overall_performance'] == PerformanceLevel.GOOD.value
        assert 'cpu' in report
        assert 'memory' in report
        assert 'disk' in report
        assert 'top_processes_cpu' in report
        assert 'top_processes_memory' in report
        assert 'bottlenecks' in report
