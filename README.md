# Code Signing Tool GUI

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-blue.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A user-friendly graphical tool for signing Windows executables and installers using PFX certificate files. This tool provides an intuitive GUI interface for batch signing multiple files with automatic Windows SDK detection and installation support.

## ✨ Features

- **Easy-to-use GUI**: Simple interface for signing multiple files
- **PFX Certificate Support**: Load your PFX certificate file with password protection
- **Batch Signing**: Sign multiple files or entire folders at once
- **Progress Logging**: Real-time output showing signing progress and results
- **Automatic SDK Installation**: Install Windows SDK directly from the tool (winget/Chocolatey)
- **Automatic signtool Detection**: Automatically finds Windows SDK's signtool.exe
- **SHA256 Signing**: Uses modern SHA256 digest algorithm
- **Timestamp Support**: Includes timestamp server for long-term signature validity

## Requirements

- **Windows 10/11** (or Windows Server)
- **Python 3.6+** (tkinter included)
- **Windows SDK** (for signtool.exe)
  - Can be installed automatically via the tool (using winget or Chocolatey)
  - Usually installed with Visual Studio
  - Or download separately from Microsoft

## Installation

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Windows SDK Installation** (if not already installed)
   - The tool will automatically detect if `signtool.exe` is installed
   - **Automatic Installation**: Click "Install Windows SDK" button in the tool
     - Uses winget (Windows Package Manager) if available
     - Falls back to Chocolatey if installed
     - Requires administrator privileges
   - **Manual Installation**: Click "Open Download Page" to download from Microsoft
     - Download Windows 10 SDK or Windows 11 SDK
     - Make sure to select "Signing Tools for Windows" component during installation
   - After installation, click "Refresh" button to detect signtool.exe

3. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/signertoolgui.git
   cd signertoolgui
   ```
   
   Or download the latest release from the [Releases](https://github.com/yourusername/signertoolgui/releases) page.

## Usage

### Running the Application

**Option 1: Double-click the launcher**
- Run `run_signer.bat` (Windows)

**Option 2: Command line**
```bash
python signertoolgui.py
```

### Signing Files

1. **Load Certificate**
   - Click "Browse..." next to "PFX Certificate File"
   - Select your `.pfx` certificate file
   - Enter the password in the password field

2. **Select Files to Sign**
   - Click "Add Files..." to select individual files
   - Click "Add Folder..." to add all executables from a folder
   - Supported file types: `.exe`, `.dll`, `.msi`, `.cab`, `.ocx`, `.sys`

3. **Sign**
   - Click "Sign Files" button
   - Monitor progress in the output log
   - Success/failure status will be displayed

### File Types Supported

- `.exe` - Executables
- `.dll` - Dynamic Link Libraries
- `.msi` - Windows Installer packages
- `.cab` - Cabinet files
- `.ocx` - ActiveX controls
- `.sys` - System drivers

## Troubleshooting

### "signtool.exe not found"
- **Use the built-in installer**: Click "Install Windows SDK" button in the tool
  - Requires winget (built into Windows 10/11) or Chocolatey
  - May require administrator privileges
- **Manual installation**: Click "Open Download Page" and download Windows SDK
  - Make sure to install "Signing Tools for Windows" component
- **After installation**: Click "Refresh" button to detect signtool.exe
- **Manual location**: You can also manually locate signtool.exe when prompted
- Ensure you have the correct architecture (x64/x86)

### "Signing failed" errors
- Verify PFX password is correct
- Ensure certificate is valid and not expired
- Check that certificate has code signing capabilities
- Verify file is not already signed (may need to remove existing signature first)
- Ensure you have write permissions to the files being signed

### Certificate Issues
- Make sure your PFX file is not corrupted
- Verify the certificate has code signing extended key usage
- Check certificate expiration date

## Technical Details

- Uses Windows SDK's `signtool.exe` for actual signing
- SHA256 digest algorithm
- RFC 3161 timestamp server (DigiCert)
- Threaded signing process for responsive UI

## 📦 Building Standalone Executable

To create a standalone executable that doesn't require Python:

```bash
build_exe.bat
```

This will create `dist/CodeSigningTool.exe` using PyInstaller.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues & Support

For issues related to:
- **signtool.exe**: Check [Windows SDK documentation](https://docs.microsoft.com/en-us/windows/win32/appxpkg/how-to-sign-a-package-using-signtool)
- **Certificates**: Contact your certificate authority
- **This tool**: [Open an issue](https://github.com/yourusername/signertoolgui/issues) in the repository

## 🙏 Acknowledgments

- Uses Windows SDK's `signtool.exe` for code signing
- Built with Python and tkinter

