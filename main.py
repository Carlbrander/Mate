import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk
import pyperclip
import pyautogui
import time

import signal
import sys
from anthropic import Anthropic
import config
import ctypes
import re

class ELI5Overlay:
    def __init__(self):
        # Main transparent window with button
        self.root = tk.Tk()
        self.root.title("Mate")
        
        # Make window transparent and always on top
        self.root.attributes('-topmost', True)  # Always on top
        
        # Remove window decorations and set transparent color
        self.root.overrideredirect(True)
        # Use a specific color for transparency on Windows
        transparent_color = '#010101'  # Near-black color to make transparent
        self.root.config(bg=transparent_color)
        self.root.wm_attributes('-transparentcolor', transparent_color)
        
        # Position more towards center-right
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = screen_width - config.BUTTON_SIZE - 100  # More towards center
        y_position = screen_height - config.BUTTON_SIZE - 150  # Higher up
        
        self.root.geometry(f"{config.BUTTON_SIZE}x{config.BUTTON_SIZE}+{x_position}+{y_position}")
        
        # Make window not steal focus on Windows using WinAPI
        self.root.update_idletasks()  # Ensure window is created
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            # Set WS_EX_NOACTIVATE extended window style
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
        except Exception as e:
            print(f"Note: Could not set no-activate style: {e}")
        
        # Create circular button using Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=config.BUTTON_SIZE,
            height=config.BUTTON_SIZE,
            bg=transparent_color,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Draw circular button with gradient-like effect
        self.button_circle = self.canvas.create_oval(
            5, 5, config.BUTTON_SIZE - 5, config.BUTTON_SIZE - 5,
            fill='#667eea',  # Modern purple-blue gradient
            outline='#764ba2',
            width=3
        )
        
        # Add shadow effect (another circle slightly offset)
        self.shadow = self.canvas.create_oval(
            8, 8, config.BUTTON_SIZE - 2, config.BUTTON_SIZE - 2,
            fill='',
            outline='#5568d3',
            width=1
        )
        self.canvas.tag_lower(self.shadow)
        
        # Add text
        self.button_text = self.canvas.create_text(
            config.BUTTON_SIZE // 2,
            config.BUTTON_SIZE // 2,
            text=config.BUTTON_TEXT,
            font=('Segoe UI', 12, 'bold'),
            fill='white'
        )
        
        # Bind events
        self.canvas.tag_bind(self.button_circle, '<Button-1>', self.start_drag)
        self.canvas.tag_bind(self.button_circle, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.button_circle, '<ButtonRelease-1>', self.on_button_click)
        self.canvas.tag_bind(self.button_text, '<Button-1>', self.start_drag)
        self.canvas.tag_bind(self.button_text, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.button_text, '<ButtonRelease-1>', self.on_button_click)
        
        # Hover effects
        self.canvas.tag_bind(self.button_circle, '<Enter>', self.on_hover)
        self.canvas.tag_bind(self.button_circle, '<Leave>', self.on_leave)
        self.canvas.tag_bind(self.button_text, '<Enter>', self.on_hover)
        self.canvas.tag_bind(self.button_text, '<Leave>', self.on_leave)
        
        # Initialize Anthropic client
        try:
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"Warning: Could not initialize Anthropic client. Please check your API key. Error: {e}")
            self.client = None
        
        # Explanation window (initially hidden)
        self.explanation_window = None
        
        # Drag tracking
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
    
    def on_hover(self, event):
        """Button hover effect"""
        self.canvas.itemconfig(self.button_circle, fill='#764ba2')
        self.root.config(cursor='hand2')
    
    def on_leave(self, event):
        """Button leave effect"""
        self.canvas.itemconfig(self.button_circle, fill='#667eea')
        self.root.config(cursor='')
    
    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = False
    
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
        self.is_dragging = True
    
    def on_button_click(self, event=None):
        # If we're dragging, don't trigger the action
        if self.is_dragging:
            self.is_dragging = False
            return
        
        if event and (abs(event.x - self.drag_start_x) > 5 or abs(event.y - self.drag_start_y) > 5):
            return
        
        # Store old clipboard content to detect changes
        old_clipboard = ""
        try:
            old_clipboard = pyperclip.paste()
            print(f"\nClipboard BEFORE Ctrl+C: '{old_clipboard}'")
        except:
            pass
        
        # Small delay to ensure click is processed
        time.sleep(0.05)
        
        # Simulate Ctrl+C to copy selected text
        print("Simulating Ctrl+C...")
        pyautogui.hotkey('ctrl', 'c')
        
        # Wait longer for clipboard to update
        time.sleep(0.2)
        
        # Get text from clipboard
        try:
            selected_text = pyperclip.paste()
            print(f"Clipboard AFTER Ctrl+C: '{selected_text}'\n")
        except Exception as e:
            self.show_explanation(f"Error reading clipboard: {str(e)}")
            return
        
        if not selected_text or selected_text.strip() == "":
            self.show_explanation("No text selected. Please select some text and try again.")
            return
        
        # Check if API key is set
        if not self.client or config.ANTHROPIC_API_KEY == "your-api-key-here":
            self.show_explanation("Please set your Anthropic API key in config.py")
            return
        
        # Show loading message
        self.show_explanation("Generating explanation...", loading=True)
        
        # Call Claude API
        try:
            explanation = self.get_eli5_explanation(selected_text)
            self.show_explanation(explanation)
        except Exception as e:
            self.show_explanation(f"Error calling Claude API: {str(e)}")
    
    def get_eli5_explanation(self, text):
        """Call Claude API to get ELI5 explanation"""
        # Build prompt from config template
        prompt = config.PROMPT_TEMPLATE.format(text=text)
        
        # Print prompt to terminal
        print("\n" + "="*60)
        print("PROMPT SENT TO CLAUDE:")
        print("="*60)
        print(prompt)
        print("="*60 + "\n")
        
        message = self.client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response = message.content[0].text
        
        # Print response to terminal
        print("="*60)
        print("RESPONSE FROM CLAUDE:")
        print("="*60)
        print(response)
        print("="*60 + "\n")
        
        return response
    
    def format_markdown_text(self, text_widget, markdown_text):
        """Format markdown text in a CTkTextbox widget"""
        # Configure text tags for different styles
        text_widget.tag_config("h1", font=("Segoe UI", 20, "bold"), spacing1=10, spacing3=5)
        text_widget.tag_config("h2", font=("Segoe UI", 17, "bold"), spacing1=8, spacing3=4)
        text_widget.tag_config("h3", font=("Segoe UI", 15, "bold"), spacing1=6, spacing3=3)
        text_widget.tag_config("bold", font=("Segoe UI", 13, "bold"))
        text_widget.tag_config("italic", font=("Segoe UI", 13, "italic"))
        text_widget.tag_config("code", font=("Consolas", 11), background="#f5f5f5", foreground="#d63384")
        text_widget.tag_config("link", font=("Segoe UI", 13, "underline"), foreground="#0066cc")
        text_widget.tag_config("bullet", font=("Segoe UI", 13))
        
        lines = markdown_text.split('\n')
        current_pos = "1.0"
        
        for line in lines:
            # Headers
            if line.startswith('# '):
                text = line[2:].strip() + '\n'
                text_widget.insert(current_pos, text, "h1")
            elif line.startswith('## '):
                text = line[3:].strip() + '\n'
                text_widget.insert(current_pos, text, "h2")
            elif line.startswith('### '):
                text = line[4:].strip() + '\n'
                text_widget.insert(current_pos, text, "h3")
            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                text = '  • ' + line[2:].strip()
                self._insert_formatted_line(text_widget, text + '\n', current_pos)
            # Code blocks (simplified - just indent them)
            elif line.startswith('```'):
                continue  # Skip code block markers
            # Normal line with inline formatting
            else:
                self._insert_formatted_line(text_widget, line + '\n', current_pos)
            
            current_pos = text_widget.index("end-1c")
    
    def _insert_formatted_line(self, text_widget, line, pos):
        """Insert a line with inline markdown formatting (bold, italic, code, links)"""
        # Process inline markdown
        remaining = line
        current_index = pos
        
        # Pattern for **bold**, *italic*, `code`, and [links](url)
        pattern = r'(\*\*.*?\*\*|\*.*?\*|`.*?`|\[.*?\]\(.*?\))'
        
        parts = re.split(pattern, remaining)
        
        for part in parts:
            if not part:
                continue
                
            # Bold: **text**
            if part.startswith('**') and part.endswith('**'):
                text = part[2:-2]
                text_widget.insert(current_index, text, "bold")
            # Italic: *text*
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                text = part[1:-1]
                text_widget.insert(current_index, text, "italic")
            # Code: `text`
            elif part.startswith('`') and part.endswith('`'):
                text = part[1:-1]
                text_widget.insert(current_index, text, "code")
            # Link: [text](url)
            elif part.startswith('[') and '](' in part:
                match = re.match(r'\[(.*?)\]\((.*?)\)', part)
                if match:
                    link_text = match.group(1)
                    text_widget.insert(current_index, link_text, "link")
                else:
                    text_widget.insert(current_index, part)
            # Normal text
            else:
                text_widget.insert(current_index, part)
            
            current_index = text_widget.index("end-1c")
    
    def show_explanation(self, text, loading=False):
        """Show explanation in a new window with CustomTkinter"""
        # Close existing explanation window if any
        if self.explanation_window and self.explanation_window.winfo_exists():
            self.explanation_window.destroy()
        
        # Create new explanation window with CustomTkinter
        self.explanation_window = ctk.CTkToplevel(self.root)
        self.explanation_window.title("")  # Empty title
        self.explanation_window.attributes('-topmost', True)
        
        # Calculate window size: smaller, 1/5 screen width, 3/5 screen height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = screen_width // 5  # Smaller width
        window_height = int(screen_height * 0.6)  # 60% of screen height
        
        # Position: top-right corner with margin from edges
        # Right side: offset from right edge
        margin_right = 20
        x_position = screen_width - window_width - margin_right
        
        # Top: offset from top edge
        margin_top = 60  # Below top bar
        y_position = margin_top
        
        self.explanation_window.geometry(
            f"{window_width}x{window_height}+{x_position}+{y_position}"
        )
        
        # Configure window appearance
        self.explanation_window.configure(fg_color="white")
        
        # Create main container with rounded corners
        main_container = ctk.CTkFrame(
            self.explanation_window,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color="#e0e0e0"
        )
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Modern header frame inside the rounded container
        header_frame = ctk.CTkFrame(
            main_container,
            fg_color="white",
            corner_radius=0,
            height=70
        )
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="mate",
            text_color="#333333",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(side='left', padx=35, pady=20)
        
        # Modern close button with hover effect
        close_button = ctk.CTkButton(
            header_frame,
            text="×",
            text_color="#999999",
            fg_color="white",
            hover_color="#f0f0f0",
            font=("Segoe UI", 28),
            width=50,
            height=50,
            corner_radius=25,
            border_width=0,
            command=self.explanation_window.destroy
        )
        close_button.pack(side='right', padx=30, pady=10)
        
        # Subtle divider line
        divider = ctk.CTkFrame(main_container, fg_color="#e8e8e8", height=1)
        divider.pack(fill='x')
        
        # Content frame for text widget
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Use standard tkinter Text widget for markdown support (CustomTkinter doesn't support tag fonts)
        text_widget = tk.Text(
            content_frame,
            wrap="word",
            font=("Segoe UI", 13),
            bg="white",
            fg="#333333",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            selectbackground='#667eea',
            selectforeground='white'
        )
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(content_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        text_widget.pack(side='left', fill='both', expand=True)
        
        # Insert text with markdown formatting
        if loading:
            text_widget.insert('1.0', text)
        else:
            self.format_markdown_text(text_widget, text)
            text_widget.config(state='disabled')  # Make read-only
    
    def run(self):
        """Start the application"""
        # Set up Ctrl+C handler
        def signal_handler(sig, frame):
            print("\nShutting down Mate Overlay...")
            self.root.quit()
            self.root.destroy()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Use a polling loop instead of mainloop for better Ctrl+C handling on Windows
        def check_for_exit():
            try:
                self.root.after(100, check_for_exit)  # Check every 100ms
            except KeyboardInterrupt:
                print("\nShutting down Mate Overlay...")
                self.root.quit()
                sys.exit(0)
        
        try:
            check_for_exit()
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down Mate Overlay...")
            self.root.quit()
            sys.exit(0)

if __name__ == "__main__":
    try:
        app = ELI5Overlay()
        print("Mate Overlay is running. Press Ctrl+C to stop.")
        app.run()
    except KeyboardInterrupt:
        print("\nApplication stopped.")
        sys.exit(0)

