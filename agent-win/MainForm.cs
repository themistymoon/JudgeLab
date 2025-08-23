using Microsoft.Extensions.Logging;
using Microsoft.Web.WebView2.WinForms;
using Microsoft.Web.WebView2.Core;
using JudgeLabAgent.Services;
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace JudgeLabAgent
{
    public partial class MainForm : Form
    {
        private readonly ILogger<MainForm> _logger;
        private readonly IConfigurationService _config;
        private readonly IIntegrityMonitor _integrityMonitor;
        private readonly INetworkService _networkService;
        
        private WebView2 _webView;
        private Label _statusLabel;
        private string _currentStatus = "Initializing...";
        
        public MainForm(
            ILogger<MainForm> logger,
            IConfigurationService config,
            IIntegrityMonitor integrityMonitor,
            INetworkService networkService)
        {
            _logger = logger;
            _config = config;
            _integrityMonitor = integrityMonitor;
            _networkService = networkService;
            
            InitializeComponent();
            
            _integrityMonitor.IntegrityChanged += OnIntegrityChanged;
        }
        
        private void InitializeComponent()
        {
            Text = "JudgeLab Secure Browser";
            Size = new Size(1200, 800);
            WindowState = FormWindowState.Maximized;
            FormBorderStyle = FormBorderStyle.None;
            TopMost = true;
            
            // Status bar
            _statusLabel = new Label
            {
                Text = _currentStatus,
                Dock = DockStyle.Bottom,
                Height = 30,
                BackColor = Color.LightGray,
                TextAlign = ContentAlignment.MiddleLeft,
                Padding = new Padding(10, 5, 10, 5)
            };
            Controls.Add(_statusLabel);
            
            // WebView2
            _webView = new WebView2
            {
                Dock = DockStyle.Fill
            };
            Controls.Add(_webView);
        }
        
        protected override async void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            
            try
            {
                // Initialize WebView2
                await _webView.EnsureCoreWebView2Async();
                _webView.CoreWebView2.Settings.AreDevToolsEnabled = false;
                _webView.CoreWebView2.Settings.AreHostObjectsAllowed = false;
                _webView.CoreWebView2.Settings.IsScriptDebuggingEnabled = false;
                _webView.CoreWebView2.Settings.AreGeneralAutofillEnabled = false;
                
                // Disable right-click context menu
                _webView.CoreWebView2.ContextMenuRequested += (s, e) => e.Handled = true;
                
                // Start monitoring
                await _integrityMonitor.StartAsync();
                
                // Navigate to allowed domain
                var defaultUrl = $"http://{_config.AllowedDomains[0]}";
                _webView.CoreWebView2.Navigate(defaultUrl);
                
                UpdateStatus("Compliant", Color.Green);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to initialize secure browser");
                UpdateStatus("Error", Color.Red);
            }
        }
        
        private void OnIntegrityChanged(object? sender, IntegrityEvent e)
        {
            Invoke(() =>
            {
                if (e.AiDetected || e.MultiDisplay)
                {
                    UpdateStatus("Flagged", Color.Red);
                }
                else
                {
                    UpdateStatus("Compliant", Color.Green);
                }
                
                // Send heartbeat to server
                _ = Task.Run(() => _networkService.SendHeartbeatAsync(e));
            });
        }
        
        private void UpdateStatus(string status, Color color)
        {
            _currentStatus = $"Status: {status} | Session: {_integrityMonitor.SessionId}";
            _statusLabel.Text = _currentStatus;
            _statusLabel.BackColor = color;
        }
        
        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (_config.ExamMode)
            {
                // Prevent closing in exam mode
                e.Cancel = true;
                MessageBox.Show("Cannot close during exam mode", "JudgeLab", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            
            _integrityMonitor?.StopAsync().GetAwaiter().GetResult();
            base.OnFormClosing(e);
        }
        
        // Prevent Alt+Tab, Alt+F4, etc.
        protected override bool ProcessCmdKey(ref Message msg, Keys keyData)
        {
            if (_config.ExamMode)
            {
                if (keyData == (Keys.Alt | Keys.Tab) ||
                    keyData == (Keys.Alt | Keys.F4) ||
                    keyData == Keys.F11)
                {
                    return true; // Block the key
                }
            }
            
            return base.ProcessCmdKey(ref msg, keyData);
        }
    }
}