import tkinter as tk
from tkinter import scrolledtext
import pyperclip
import pyautogui
import time
import signal
import sys
from anthropic import Anthropic
import config
import ctypes

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
    
    def show_explanation(self, text, loading=False):
        """Show explanation in a new window"""
        # Close existing explanation window if any
        if self.explanation_window and self.explanation_window.winfo_exists():
            self.explanation_window.destroy()
        
        # Create new explanation window
        self.explanation_window = tk.Toplevel(self.root)
        self.explanation_window.overrideredirect(True)  # Remove default border
        self.explanation_window.attributes('-topmost', True)
        
        # Position in bottom right, above the button
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = screen_width - config.EXPLANATION_WINDOW_WIDTH - 20
        y_position = screen_height - config.EXPLANATION_WINDOW_HEIGHT - 120
        
        self.explanation_window.geometry(
            f"{config.EXPLANATION_WINDOW_WIDTH}x{config.EXPLANATION_WINDOW_HEIGHT}+{x_position}+{y_position}"
        )
        
        # Main container with padding for shadow effect
        main_container = tk.Frame(self.explanation_window, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True)
        
        # Inner frame with border for modern look
        inner_frame = tk.Frame(
            main_container,
            bg='white',
            highlightbackground='#e0e0e0',
            highlightthickness=1
        )
        inner_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Modern header with gradient-like appearance
        header_frame = tk.Frame(inner_frame, bg='white', height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="mate",
            bg='white',
            fg='#333333',
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(side='left', padx=35, pady=20)
        
        # Modern minimalist close button
        close_button = tk.Label(
            header_frame,
            text="×",
            bg='white',
            fg='#999999',
            font=('Segoe UI', 28),
            cursor='hand2',
            padx=15
        )
        close_button.pack(side='right', padx=30)
        close_button.bind('<Enter>', lambda e: close_button.config(fg='#333333', bg='#f0f0f0'))
        close_button.bind('<Leave>', lambda e: close_button.config(fg='#999999', bg='white'))
        close_button.bind('<Button-1>', lambda e: self.explanation_window.destroy())
        
        # Subtle divider line
        divider = tk.Frame(inner_frame, bg='#e8e8e8', height=1)
        divider.pack(fill='x')
        
        # Content frame with padding
        content_frame = tk.Frame(inner_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Create text widget with modern styling
        text_widget = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 13),
            bg='white',
            fg='#333333',
            relief='flat',
            padx=40,
            pady=30,
            spacing1=2,  # Space before paragraph
            spacing2=1,  # Space between lines
            spacing3=4,  # Space after paragraph
            borderwidth=0,
            highlightthickness=0,
            selectbackground='#667eea',
            selectforeground='white'
        )
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', text)
        
        # Style the scrollbar
        try:
            # Configure scrollbar colors if possible
            text_widget.vbar.config(
                bg='white',
                troughcolor='#f5f5f5',
                relief='flat',
                width=16
            )
        except:
            pass
        
        if not loading:
            text_widget.config(state='disabled')  # Make read-only
        
        # Add drop shadow effect (simulation with frames)
        try:
            # Windows shadow effect
            self.explanation_window.attributes('-alpha', 0.98)
        except:
            pass
    
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

