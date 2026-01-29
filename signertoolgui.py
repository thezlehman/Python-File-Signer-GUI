#!/usr/bin/env python3
"""
Code Signing Tool GUI
A distribution-ready tool for signing Windows executables using PFX certificates.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import webbrowser
from pathlib import Path


class SigningToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Signing Tool")
        self.root.geometry("800x750")
        self.root.minsize(750, 700)
        self.root.resizable(True, True)
        
        # Variables
        self.pfx_path = tk.StringVar()
        self.pfx_password = tk.StringVar()
        self.selected_files = []
        self.signtool_path = None
        self.sdk_status_label = None
        
        # Find signtool.exe (will be called again after widgets are created)
        self.find_signtool()
        
        self.create_widgets()
        
        # Update SDK status after widgets are created
        self.update_sdk_status()
        
    def find_signtool(self):
        """Find signtool.exe in common Windows SDK locations"""
        common_paths = [
            # Windows 10/11 SDK - x64
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
            # Windows 10/11 SDK - x86
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x86\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x86\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x86\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\x86\signtool.exe",
            # Alternative locations
            r"C:\Program Files\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files\Windows Kits\10\bin\x86\signtool.exe",
        ]
        
        # Also check in PATH
        try:
            result = subprocess.run(
                ["where", "signtool.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                if os.path.exists(path):
                    self.signtool_path = path
                    return
        except:
            pass
        
        # Check common paths
        for path in common_paths:
            if os.path.exists(path):
                self.signtool_path = path
                return
        
        # If not found, will prompt user later
        self.signtool_path = None
    
    def refresh_sdk_status(self):
        """Refresh SDK detection and update status"""
        self.log("\nRefreshing SDK detection...")
        self.find_signtool()
        self.update_sdk_status()
        if self.signtool_path:
            self.log(f"✓ Found signtool.exe at: {self.signtool_path}")
        else:
            self.log("✗ signtool.exe still not found")
    
    def update_sdk_status(self):
        """Update SDK status display"""
        if self.signtool_path:
            # Truncate long paths for display
            display_path = self.signtool_path
            if len(display_path) > 60:
                display_path = "..." + display_path[-57:]
            self.sdk_status_label.config(
                text=f"✓ Windows SDK Found: {display_path}",
                foreground="green"
            )
            self.sdk_install_button.config(state=tk.DISABLED)
            self.sdk_download_button.config(state=tk.NORMAL)
        else:
            self.sdk_status_label.config(
                text="✗ Windows SDK Not Found - signtool.exe is required",
                foreground="red"
            )
            self.sdk_install_button.config(state=tk.NORMAL)
            self.sdk_download_button.config(state=tk.NORMAL)
    
    def check_winget_available(self):
        """Check if winget (Windows Package Manager) is available"""
        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def check_choco_available(self):
        """Check if Chocolatey is available"""
        try:
            result = subprocess.run(
                ["choco", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def install_sdk(self):
        """Attempt to install Windows SDK"""
        if not messagebox.askyesno(
            "Install Windows SDK",
            "This will attempt to install Windows SDK using winget or Chocolatey.\n\n"
            "Administrator privileges may be required.\n\n"
            "Continue?"
        ):
            return
        
        self.log("\n=== Attempting to install Windows SDK ===")
        
        # Try winget first (built into Windows 10/11)
        if self.check_winget_available():
            self.log("Found winget. Attempting to install Windows SDK...")
            self.log("Note: Administrator privileges may be required.")
            
            def install_thread():
                try:
                    # Install Windows 10 SDK (includes signtool)
                    cmd = [
                        "winget", "install",
                        "--id", "Microsoft.WindowsSDK.10",
                        "--accept-package-agreements",
                        "--accept-source-agreements",
                        "--silent"
                    ]
                    
                    self.log("Running: winget install Microsoft.WindowsSDK.10")
                    self.log("This may take several minutes...")
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Stream output
                    for line in process.stdout:
                        self.log(line.strip())
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        self.log("\n✓ Windows SDK installation completed!")
                        self.log("Please restart this application to detect signtool.exe")
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Installation Complete",
                            "Windows SDK installation completed!\n\n"
                            "Please restart this application to detect signtool.exe"
                        ))
                    else:
                        self.log("\n✗ Installation may have failed. Check output above.")
                        self.root.after(0, lambda: messagebox.showwarning(
                            "Installation",
                            "Installation completed with warnings.\n\n"
                            "Please check the output log and try restarting the application."
                        ))
                        
                except Exception as e:
                    self.log(f"\n✗ Error during installation: {str(e)}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Installation Error",
                        f"Error during installation:\n{str(e)}\n\n"
                        "You may need to install Windows SDK manually."
                    ))
            
            thread = threading.Thread(target=install_thread)
            thread.daemon = True
            thread.start()
            return
        
        # Try Chocolatey
        if self.check_choco_available():
            self.log("Found Chocolatey. Attempting to install Windows SDK...")
            self.log("Note: Administrator privileges may be required.")
            
            def install_thread():
                try:
                    cmd = [
                        "choco", "install", "windows-sdk-10.1",
                        "-y", "--no-progress"
                    ]
                    
                    self.log("Running: choco install windows-sdk-10.1")
                    self.log("This may take several minutes...")
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    for line in process.stdout:
                        self.log(line.strip())
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        self.log("\n✓ Windows SDK installation completed!")
                        self.log("Please restart this application to detect signtool.exe")
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Installation Complete",
                            "Windows SDK installation completed!\n\n"
                            "Please restart this application to detect signtool.exe"
                        ))
                    else:
                        self.log("\n✗ Installation may have failed. Check output above.")
                        self.root.after(0, lambda: messagebox.showwarning(
                            "Installation",
                            "Installation completed with warnings.\n\n"
                            "Please check the output log."
                        ))
                        
                except Exception as e:
                    self.log(f"\n✗ Error during installation: {str(e)}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Installation Error",
                        f"Error during installation:\n{str(e)}"
                    ))
            
            thread = threading.Thread(target=install_thread)
            thread.daemon = True
            thread.start()
            return
        
        # No package manager found
        self.log("\n✗ No package manager (winget/choco) found.")
        self.log("Opening download page for manual installation...")
        messagebox.showinfo(
            "Manual Installation Required",
            "No automatic package manager found.\n\n"
            "Opening Windows SDK download page in your browser.\n\n"
            "After downloading and installing, restart this application."
        )
        self.open_sdk_download_page()
    
    def open_sdk_download_page(self):
        """Open Windows SDK download page in browser"""
        url = "https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/"
        self.log(f"\nOpening download page: {url}")
        webbrowser.open(url)
        messagebox.showinfo(
            "Download Page",
            "Windows SDK download page opened in your browser.\n\n"
            "Download and install:\n"
            "- Windows 10 SDK (or Windows 11 SDK)\n"
            "- Make sure to select 'Signing Tools for Windows' component\n\n"
            "After installation, restart this application."
        )
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Code Signing Tool",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        # SDK Status Section
        sdk_frame = ttk.LabelFrame(main_frame, text="Windows SDK Status", padding="8")
        sdk_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=3)
        sdk_frame.columnconfigure(0, weight=1)
        
        # Status label on first row
        status_label_frame = ttk.Frame(sdk_frame)
        status_label_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=3)
        
        self.sdk_status_label = ttk.Label(
            status_label_frame,
            text="Checking SDK status...",
            foreground="orange"
        )
        self.sdk_status_label.pack(side=tk.LEFT)
        
        # Buttons on second row, wrapped
        button_frame = ttk.Frame(sdk_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=3)
        
        self.sdk_install_button = ttk.Button(
            button_frame,
            text="Install SDK",
            command=self.install_sdk,
            state=tk.DISABLED,
            width=12
        )
        self.sdk_install_button.pack(side=tk.LEFT, padx=2)
        
        self.sdk_download_button = ttk.Button(
            button_frame,
            text="Download Page",
            command=self.open_sdk_download_page,
            width=15
        )
        self.sdk_download_button.pack(side=tk.LEFT, padx=2)
        
        self.sdk_refresh_button = ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_sdk_status,
            width=12
        )
        self.sdk_refresh_button.pack(side=tk.LEFT, padx=2)
        
        # PFX Certificate Section
        cert_frame = ttk.LabelFrame(main_frame, text="Certificate Settings", padding="8")
        cert_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=3)
        cert_frame.columnconfigure(1, weight=1)
        
        # PFX File
        ttk.Label(cert_frame, text="PFX File:", width=12).grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Entry(cert_frame, textvariable=self.pfx_path).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=3, pady=3)
        ttk.Button(cert_frame, text="Browse...", command=self.browse_pfx, width=10).grid(row=0, column=2, padx=3, pady=3)
        
        # Password
        ttk.Label(cert_frame, text="Password:", width=12).grid(row=1, column=0, sticky=tk.W, pady=3)
        password_entry = ttk.Entry(cert_frame, textvariable=self.pfx_password, show="*")
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=3, pady=3)
        
        # Files to Sign Section
        files_frame = ttk.LabelFrame(main_frame, text="Files to Sign", padding="8")
        files_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=3)
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # File list buttons
        button_frame = ttk.Frame(files_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=3)
        
        ttk.Button(button_frame, text="Add Files", command=self.add_files, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Add Folder", command=self.add_folder, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Remove", command=self.remove_selected, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_files, width=12).pack(side=tk.LEFT, padx=2)
        
        # File listbox with scrollbar
        listbox_frame = ttk.Frame(files_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Output/Log Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="8")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=3)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=6, wrap=tk.WORD, font=("Consolas", 9))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sign Button
        sign_button = ttk.Button(main_frame, text="Sign Files", command=self.sign_files, style="Accent.TButton")
        sign_button.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, padding=3)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=3)
        
        self.log("Code Signing Tool initialized")
        if self.signtool_path:
            self.log(f"Found signtool.exe at: {self.signtool_path}")
        else:
            self.log("WARNING: signtool.exe not found. Please install Windows SDK.")
    
    def browse_pfx(self):
        filename = filedialog.askopenfilename(
            title="Select PFX Certificate File",
            filetypes=[("PFX Files", "*.pfx"), ("All Files", "*.*")]
        )
        if filename:
            self.pfx_path.set(filename)
            self.log(f"Selected PFX file: {filename}")
    
    def add_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select Files to Sign",
            filetypes=[
                ("Executables", "*.exe *.dll *.msi *.cab *.ocx *.sys"),
                ("All Files", "*.*")
            ]
        )
        for filename in filenames:
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self.file_listbox.insert(tk.END, filename)
        self.log(f"Added {len(filenames)} file(s)")
    
    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            # Find common executable files
            extensions = ['.exe', '.dll', '.msi', '.cab', '.ocx', '.sys']
            added = 0
            for ext in extensions:
                for filepath in Path(folder).rglob(f'*{ext}'):
                    filepath_str = str(filepath)
                    if filepath_str not in self.selected_files:
                        self.selected_files.append(filepath_str)
                        self.file_listbox.insert(tk.END, filepath_str)
                        added += 1
            self.log(f"Added {added} file(s) from folder")
    
    def remove_selected(self):
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            self.selected_files.pop(index)
            self.file_listbox.delete(index)
        self.log(f"Removed {len(selected_indices)} file(s)")
    
    def clear_files(self):
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.log("Cleared all files")
    
    def log(self, message):
        """Add message to output log"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def sign_files(self):
        """Sign all selected files"""
        # Validation
        if not self.pfx_path.get():
            messagebox.showerror("Error", "Please select a PFX certificate file.")
            return
        
        if not os.path.exists(self.pfx_path.get()):
            messagebox.showerror("Error", "PFX file does not exist.")
            return
        
        if not self.pfx_password.get():
            messagebox.showwarning("Warning", "No password provided. Continuing anyway...")
        
        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one file to sign.")
            return
        
        if not self.signtool_path:
            # Try to find signtool again
            self.find_signtool()
            if not self.signtool_path:
                # Offer to install SDK or locate manually
                response = messagebox.askyesnocancel(
                    "signtool.exe Not Found",
                    "signtool.exe is required to sign files.\n\n"
                    "Would you like to:\n"
                    "- YES: Install Windows SDK automatically\n"
                    "- NO: Locate signtool.exe manually\n"
                    "- CANCEL: Cancel signing"
                )
                
                if response is True:  # Yes - install SDK
                    self.install_sdk()
                    return
                elif response is False:  # No - locate manually
                    signtool_path = filedialog.askopenfilename(
                        title="Locate signtool.exe",
                        filetypes=[("Executable", "signtool.exe"), ("All Files", "*.*")]
                    )
                    if signtool_path and os.path.exists(signtool_path):
                        self.signtool_path = signtool_path
                        self.update_sdk_status()
                    else:
                        messagebox.showerror(
                            "Error",
                            "signtool.exe not found. Please install Windows SDK or locate signtool.exe manually."
                        )
                        return
                else:  # Cancel
                    return
        
        # Disable sign button during signing
        self.status_var.set("Signing files...")
        self.root.update()
        
        # Run signing in a separate thread to keep UI responsive
        thread = threading.Thread(target=self._sign_files_thread)
        thread.daemon = True
        thread.start()
    
    def _sign_files_thread(self):
        """Sign files in a separate thread"""
        pfx_file = self.pfx_path.get()
        password = self.pfx_password.get()
        
        success_count = 0
        fail_count = 0
        
        for file_path in self.selected_files:
            if not os.path.exists(file_path):
                self.log(f"ERROR: File not found: {file_path}")
                fail_count += 1
                continue
            
            try:
                self.log(f"\nSigning: {file_path}")
                
                # Build signtool command
                cmd = [
                    self.signtool_path,
                    "sign",
                    "/f", pfx_file,
                    "/p", password,
                    "/fd", "SHA256",  # Use SHA256 digest algorithm
                    "/tr", "http://timestamp.digicert.com",  # RFC 3161 timestamp server
                    "/td", "SHA256",
                    "/v",  # Verbose output
                    file_path
                ]
                
                # Run signtool
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per file
                )
                
                if result.returncode == 0:
                    self.log(f"✓ Successfully signed: {os.path.basename(file_path)}")
                    success_count += 1
                else:
                    error_msg = result.stderr or result.stdout
                    self.log(f"✗ Failed to sign: {os.path.basename(file_path)}")
                    self.log(f"  Error: {error_msg}")
                    fail_count += 1
                    
            except subprocess.TimeoutExpired:
                self.log(f"✗ Timeout signing: {os.path.basename(file_path)}")
                fail_count += 1
            except Exception as e:
                self.log(f"✗ Exception signing {os.path.basename(file_path)}: {str(e)}")
                fail_count += 1
        
        # Update status
        self.root.after(0, lambda: self.status_var.set(
            f"Complete: {success_count} succeeded, {fail_count} failed"
        ))
        
        if fail_count == 0:
            self.log("\n✓ All files signed successfully!")
            self.root.after(0, lambda: messagebox.showinfo("Success", f"All {success_count} file(s) signed successfully!"))
        else:
            self.log(f"\n⚠ Signing complete with {fail_count} error(s)")
            self.root.after(0, lambda: messagebox.showwarning(
                "Signing Complete",
                f"Signed {success_count} file(s) successfully.\n{fail_count} file(s) failed."
            ))


def main():
    root = tk.Tk()
    app = SigningToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

