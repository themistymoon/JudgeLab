using Microsoft.Extensions.Configuration;
using System.Collections.Generic;
using System.Linq;

namespace JudgeLabAgent.Services
{
    public class ConfigurationService : IConfigurationService
    {
        private readonly IConfiguration _configuration;
        
        public ConfigurationService(IConfiguration configuration)
        {
            _configuration = configuration;
        }
        
        public string ApiUrl => _configuration["JudgeLab:ApiUrl"] ?? "http://localhost:8000/api/v1";
        
        public List<string> AllowedDomains => 
            _configuration.GetSection("JudgeLab:AllowedDomains").Get<List<string>>() ?? new List<string>();
        
        public int HeartbeatIntervalSeconds => 
            _configuration.GetValue<int>("JudgeLab:HeartbeatIntervalSeconds", 10);
        
        public int OfflineQueueMaxSize => 
            _configuration.GetValue<int>("JudgeLab:OfflineQueueMaxSize", 1000);
        
        public bool ExamMode => 
            _configuration.GetValue<bool>("JudgeLab:ExamMode", true);
        
        public bool BlockScreenshot => 
            _configuration.GetValue<bool>("JudgeLab:BlockScreenshot", true);
        
        public bool BlockClipboard => 
            _configuration.GetValue<bool>("JudgeLab:BlockClipboard", true);
        
        public bool DetectAI => 
            _configuration.GetValue<bool>("JudgeLab:DetectAI", true);
        
        public bool RequireSingleDisplay => 
            _configuration.GetValue<bool>("JudgeLab:RequireSingleDisplay", true);
        
        public List<string> AllowedProcesses => 
            _configuration.GetSection("JudgeLab:AllowedProcesses").Get<List<string>>() ?? new List<string>();
    }
}