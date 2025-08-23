using System;
using System.Threading.Tasks;

namespace JudgeLabAgent.Services
{
    public class IntegrityEvent
    {
        public string SessionId { get; set; } = "";
        public DateTime Timestamp { get; set; }
        public bool AiDetected { get; set; }
        public bool MultiDisplay { get; set; }
        public int ClipboardBlocked { get; set; }
        public int PrintScreenBlocked { get; set; }
        public object? Sources { get; set; }
        public string AppVersion { get; set; } = "";
    }
    
    public interface IIntegrityMonitor
    {
        event EventHandler<IntegrityEvent>? IntegrityChanged;
        
        string SessionId { get; }
        string Status { get; }
        
        Task StartAsync();
        Task StopAsync();
        
        IntegrityEvent GetCurrentState();
    }
}