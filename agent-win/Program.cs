using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using JudgeLabAgent.Services;
using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace JudgeLabAgent
{
    internal static class Program
    {
        /// <summary>
        ///  The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            
            // Configure services
            var services = ConfigureServices();
            var serviceProvider = services.BuildServiceProvider();
            
            var loggerFactory = serviceProvider.GetRequiredService<ILoggerFactory>();
            var logger = loggerFactory.CreateLogger("JudgeLabAgent");
            logger.LogInformation("JudgeLab Agent starting...");
            
            try
            {
                var mainForm = serviceProvider.GetRequiredService<MainForm>();
                Application.Run(mainForm);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Unhandled exception in main application");
                MessageBox.Show($"Fatal error: {ex.Message}", "JudgeLab Agent", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                serviceProvider.Dispose();
            }
        }
        
        private static ServiceCollection ConfigureServices()
        {
            var services = new ServiceCollection();
            
            // Configuration
            var configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                .Build();
            
            services.AddSingleton<IConfiguration>(configuration);
            
            // Logging
            services.AddLogging(builder =>
            {
                builder.AddConsole();
                builder.SetMinimumLevel(LogLevel.Information);
            });
            
            // Services
            services.AddSingleton<IConfigurationService, ConfigurationService>();
            services.AddSingleton<IIntegrityMonitor, IntegrityMonitor>();
            services.AddSingleton<INetworkService, NetworkService>();
            services.AddSingleton<IDisplayMonitor, DisplayMonitor>();
            services.AddSingleton<IKeyboardHook, KeyboardHook>();
            services.AddSingleton<IProcessMonitor, ProcessMonitor>();
            
            // Main form
            services.AddTransient<MainForm>();
            
            return services;
        }
    }
}