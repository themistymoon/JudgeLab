using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace JudgeLabAgent.Services
{
    public class IntegrityMonitor : IIntegrityMonitor, IDisposable
    {
        private readonly ILogger<IntegrityMonitor> _logger;
        private readonly IConfigurationService _config;
        private readonly IDisplayMonitor _displayMonitor;
        private readonly IKeyboardHook _keyboardHook;
        private readonly IProcessMonitor _processMonitor;
        
        private Timer? _monitorTimer;
        private bool _disposed = false;
        
        public event EventHandler<IntegrityEvent>? IntegrityChanged;
        
        public string SessionId { get; }
        public string Status { get; private set; } = "Disconnected";
        
        public IntegrityMonitor(
            ILogger<IntegrityMonitor> logger,
            IConfigurationService config,
            IDisplayMonitor displayMonitor,
            IKeyboardHook keyboardHook,
            IProcessMonitor processMonitor)
        {
            _logger = logger;
            _config = config;
            _displayMonitor = displayMonitor;
            _keyboardHook = keyboardHook;
            _processMonitor = processMonitor;
            
            SessionId = Guid.NewGuid().ToString("N")[..16];
        }
        
        public async Task StartAsync()
        {
            _logger.LogInformation("Starting integrity monitoring for session {SessionId}", SessionId);
            
            // Start sub-monitors
            await _displayMonitor.StartAsync();
            await _keyboardHook.StartAsync();
            await _processMonitor.StartAsync();
            
            // Start periodic monitoring
            _monitorTimer = new Timer(
                MonitorCallback,
                null,
                TimeSpan.Zero,
                TimeSpan.FromSeconds(_config.HeartbeatIntervalSeconds)
            );
            
            Status = "Active";
        }
        
        public async Task StopAsync()
        {
            _logger.LogInformation("Stopping integrity monitoring");
            
            _monitorTimer?.Dispose();
            _monitorTimer = null;
            
            await _displayMonitor.StopAsync();
            await _keyboardHook.StopAsync();
            await _processMonitor.StopAsync();
            
            Status = "Stopped";
        }
        
        private void MonitorCallback(object? state)
        {
            try
            {
                var integrityEvent = GetCurrentState();
                IntegrityChanged?.Invoke(this, integrityEvent);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during integrity monitoring");
            }
        }
        
        public IntegrityEvent GetCurrentState()
        {
            var displayInfo = _displayMonitor.GetDisplayInfo();
            var blockedEvents = _keyboardHook.GetBlockedCounts();
            var aiDetected = _processMonitor.IsAIDetected();
            
            return new IntegrityEvent
            {
                SessionId = SessionId,
                Timestamp = DateTime.UtcNow,
                AiDetected = aiDetected,
                MultiDisplay = displayInfo.Count > 1,
                ClipboardBlocked = blockedEvents.ClipboardBlocked,
                PrintScreenBlocked = blockedEvents.PrintScreenBlocked,
                Sources = _processMonitor.GetDetectedSources(),
                AppVersion = "0.1.0"
            };
        }
        
        public void Dispose()
        {
            if (!_disposed)
            {
                StopAsync().GetAwaiter().GetResult();
                _disposed = true;
            }
        }
    }
}