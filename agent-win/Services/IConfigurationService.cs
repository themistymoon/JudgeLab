using System.Collections.Generic;

namespace JudgeLabAgent.Services
{
    public interface IConfigurationService
    {
        string ApiUrl { get; }
        List<string> AllowedDomains { get; }
        int HeartbeatIntervalSeconds { get; }
        int OfflineQueueMaxSize { get; }
        bool ExamMode { get; }
        bool BlockScreenshot { get; }
        bool BlockClipboard { get; }
        bool DetectAI { get; }
        bool RequireSingleDisplay { get; }
        List<string> AllowedProcesses { get; }
    }
}