import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

class RichTextEditor(scrolledtext.ScrolledText):
    """Enhanced text editor with real-time formatting support"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_formatting_tags()
        self.bind('<KeyRelease>', self._on_text_changed)
        
    def _setup_formatting_tags(self):
        """Configure text styling tags for different formatting types"""
        self.tag_configure('bold', font=('Segoe UI', 10, 'bold'))
        self.tag_configure('italic', font=('Segoe UI', 10, 'italic'))
        self.tag_configure('underline', underline=True)
        self.tag_configure('heading', font=('Segoe UI', 12, 'bold'), foreground='#2c3e50')
        self.tag_configure('chapter_separator', font=('Segoe UI', 11, 'bold'), 
                          foreground='#34495e', background='#ecf0f1')
        
    def _on_text_changed(self, event=None):
        """Apply formatting when text content changes"""
        self._apply_text_formatting()
        
    def _apply_text_formatting(self):
        """Parse and apply markdown-style formatting to text"""
        content = self.get(1.0, tk.END)
        
        # Clear existing formatting
        for tag in ['bold', 'italic', 'underline', 'heading', 'chapter_separator']:
            self.tag_remove(tag, 1.0, tk.END)
        
        # Apply chapter separators (=== Chapter Title ===)
        separator_pattern = r'^=== (.+?) ===$'
        for match in re.finditer(separator_pattern, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.tag_add('chapter_separator', start, end)
            
        # Apply headings (# Heading)
        heading_pattern = r'^#\s+(.+)$'
        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.tag_add('heading', start, end)
            
        # Apply bold formatting (**text**)
        bold_pattern = r'\*\*(.+?)\*\*'
        for match in re.finditer(bold_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.tag_add('bold', start, end)
            
        # Apply italic formatting (*text*)
        italic_pattern = r'\*(.+?)\*'
        for match in re.finditer(italic_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.tag_add('italic', start, end)
            
        # Apply underline formatting (__text__)
        underline_pattern = r'__(.+?)__'
        for match in re.finditer(underline_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.tag_add('underline', start, end)

class EpubEditor:
    """Main EPUB editor application with professional Windows UI"""
    
    def __init__(self, root):
        self.root = root
        self._configure_window()
        self._initialize_data()
        self._build_interface()
        self._apply_windows_theme()
        
    def _configure_window(self):
        """Set up the main window properties"""
        self.root.title("EPUB Editor")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Set window icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
    def _initialize_data(self):
        """Initialize application data structures"""
        self.current_book = None
        self.current_book_path = None
        self.chapters = []
        self.current_chapter_index = 0
        self.view_mode = "chapter"  # "chapter" or "full_book"
        
    def _build_interface(self):
        """Construct the main application interface"""
        self._create_menu_bar()
        self._create_toolbar()
        self._create_main_layout()
        self._create_content_panels()
        self._bind_shortcuts()
        
    def _create_menu_bar(self):
        """Build the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open EPUB...", command=self._open_epub, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._save_epub, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_epub_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self._find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self._replace_text, accelerator="Ctrl+H")
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=lambda: self._insert_format('**', '**'), accelerator="Ctrl+B")
        format_menu.add_command(label="Italic", command=lambda: self._insert_format('*', '*'), accelerator="Ctrl+I")
        format_menu.add_command(label="Underline", command=lambda: self._insert_format('__', '__'), accelerator="Ctrl+U")
        format_menu.add_command(label="Heading", command=lambda: self._insert_format('# ', ''), accelerator="Ctrl+H")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Chapter View", command=lambda: self._switch_view_mode("chapter"), accelerator="Ctrl+1")
        view_menu.add_command(label="Full Book View", command=lambda: self._switch_view_mode("full_book"), accelerator="Ctrl+2")
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Chapter Panel", command=self._toggle_chapter_panel)
        view_menu.add_command(label="Full Screen", command=self._toggle_fullscreen, accelerator="F11")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _create_toolbar(self):
        """Create the main toolbar with common actions"""
        toolbar_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        toolbar_frame.pack(fill=tk.X, padx=2, pady=1)
        
        # File operations section
        file_frame = ttk.Frame(toolbar_frame)
        file_frame.pack(side=tk.LEFT, padx=5, pady=2)
        
        ttk.Button(file_frame, text="Open", command=self._open_epub, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(file_frame, text="Save", command=self._save_epub, width=8).pack(side=tk.LEFT, padx=1)
        
        # Navigation section
        nav_frame = ttk.Frame(toolbar_frame)
        nav_frame.pack(side=tk.LEFT, padx=10, pady=2)
        
        ttk.Button(nav_frame, text="← Previous", command=self._previous_chapter, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="Next →", command=self._next_chapter, width=10).pack(side=tk.LEFT, padx=1)
        
        # View mode section
        view_frame = ttk.Frame(toolbar_frame)
        view_frame.pack(side=tk.LEFT, padx=10, pady=2)
        
        ttk.Label(view_frame, text="View Mode:").pack(side=tk.LEFT, padx=2)
        self.view_mode_var = tk.StringVar(value="Chapter")
        view_combo = ttk.Combobox(view_frame, textvariable=self.view_mode_var, 
                                 values=["Chapter", "Full Book"], 
                                 state="readonly", width=12)
        view_combo.pack(side=tk.LEFT, padx=2)
        view_combo.bind('<<ComboboxSelected>>', self._on_view_mode_changed)
        
        # Formatting section
        format_frame = ttk.Frame(toolbar_frame)
        format_frame.pack(side=tk.LEFT, padx=10, pady=2)
        
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT, padx=2)
        ttk.Button(format_frame, text="B", command=lambda: self._insert_format('**', '**'), 
                  width=3, style='Bold.TButton').pack(side=tk.LEFT, padx=1)
        ttk.Button(format_frame, text="I", command=lambda: self._insert_format('*', '*'), 
                  width=3, style='Italic.TButton').pack(side=tk.LEFT, padx=1)
        ttk.Button(format_frame, text="U", command=lambda: self._insert_format('__', '__'), 
                  width=3, style='Underline.TButton').pack(side=tk.LEFT, padx=1)
        ttk.Button(format_frame, text="H", command=lambda: self._insert_format('# ', ''), 
                  width=3, style='Heading.TButton').pack(side=tk.LEFT, padx=1)
        
        # Status section
        status_frame = ttk.Frame(toolbar_frame)
        status_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=('Segoe UI', 8))
        self.status_label.pack(side=tk.RIGHT)
        
    def _create_main_layout(self):
        """Set up the main application layout"""
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Left panel for navigation and metadata
        self.left_panel = ttk.Frame(self.main_paned, width=280)
        self.main_paned.add(self.left_panel, weight=1)
        
        # Right panel for the editor
        self.right_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_panel, weight=3)
        
    def _create_content_panels(self):
        """Create the content panels for navigation and editing"""
        self._create_navigation_panel()
        self._create_editor_panel()
        
    def _create_navigation_panel(self):
        """Build the left navigation panel"""
        # Book information section
        info_frame = ttk.LabelFrame(self.left_panel, text="Book Information", padding=8)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="Title:").pack(anchor=tk.W)
        self.book_title_label = ttk.Label(info_frame, text="No book loaded", 
                                         font=("Segoe UI", 9, "bold"))
        self.book_title_label.pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(info_frame, text="Author:").pack(anchor=tk.W)
        self.book_author_label = ttk.Label(info_frame, text="Unknown")
        self.book_author_label.pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(info_frame, text="Chapters:").pack(anchor=tk.W)
        self.chapter_count_label = ttk.Label(info_frame, text="0")
        self.chapter_count_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Current view indicator
        ttk.Label(info_frame, text="Current View:").pack(anchor=tk.W)
        self.view_mode_label = ttk.Label(info_frame, text="Chapter View", 
                                        font=("Segoe UI", 8, "bold"), foreground="#2980b9")
        self.view_mode_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Chapter navigation section
        chapter_frame = ttk.LabelFrame(self.left_panel, text="Chapters", padding=8)
        chapter_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chapter list with scrollbar
        list_container = ttk.Frame(chapter_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.chapter_listbox = tk.Listbox(list_container, selectmode=tk.SINGLE, 
                                         font=("Segoe UI", 9), relief=tk.SUNKEN, borderwidth=1)
        self.chapter_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        chapter_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                         command=self.chapter_listbox.yview)
        chapter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chapter_listbox.config(yscrollcommand=chapter_scrollbar.set)
        
        self.chapter_listbox.bind('<<ListboxSelect>>', self._on_chapter_selected)
        
    def _create_editor_panel(self):
        """Create the main text editor panel"""
        # Editor header
        editor_header = ttk.Frame(self.right_panel)
        editor_header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(editor_header, text="Editor", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        
        # Formatting help
        help_text = "Formatting: **bold** *italic* __underline__ # heading"
        ttk.Label(editor_header, text=help_text, font=("Segoe UI", 8), 
                 foreground="#7f8c8d").pack(side=tk.RIGHT)
        
        # Main text editor
        self.editor_text = RichTextEditor(self.right_panel, 
                                        wrap=tk.WORD, 
                                        font=("Segoe UI", 10),
                                        undo=True,
                                        relief=tk.SUNKEN,
                                        borderwidth=1)
        self.editor_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _apply_windows_theme(self):
        """Apply Windows-style theming to the application"""
        style = ttk.Style()
        
        # Use Windows theme if available
        try:
            style.theme_use('vista')
        except:
            try:
                style.theme_use('clam')
            except:
                pass
        
        # Configure custom button styles
        style.configure('Bold.TButton', font=('Segoe UI', 8, 'bold'))
        style.configure('Italic.TButton', font=('Segoe UI', 8, 'italic'))
        style.configure('Underline.TButton', font=('Segoe UI', 8, 'normal'), underline=True)
        style.configure('Heading.TButton', font=('Segoe UI', 8, 'bold'))
        
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts to application functions"""
        self.root.bind('<Control-o>', lambda e: self._open_epub())
        self.root.bind('<Control-s>', lambda e: self._save_epub())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.root.bind('<Control-b>', lambda e: self._insert_format('**', '**'))
        self.root.bind('<Control-i>', lambda e: self._insert_format('*', '*'))
        self.root.bind('<Control-u>', lambda e: self._insert_format('__', '__'))
        self.root.bind('<Control-Key-1>', lambda e: self._switch_view_mode("chapter"))
        self.root.bind('<Control-Key-2>', lambda e: self._switch_view_mode("full_book"))
        
    def _switch_view_mode(self, mode):
        """Switch between chapter view and full book view"""
        if mode == self.view_mode:
            return
            
        self.view_mode = mode
        
        if mode == "chapter":
            self.view_mode_var.set("Chapter")
            self.view_mode_label.config(text="Chapter View", foreground="#2980b9")
            if self.chapters:
                self._load_chapter(self.current_chapter_index)
        else:  # full_book
            self.view_mode_var.set("Full Book")
            self.view_mode_label.config(text="Full Book View", foreground="#27ae60")
            self._load_full_book()
            
        self._update_status(f"Switched to {mode.replace('_', ' ')} view")
    
    def _on_view_mode_changed(self, event):
        """Handle view mode change from toolbar dropdown"""
        mode = self.view_mode_var.get()
        if mode == "Chapter":
            self._switch_view_mode("chapter")
        else:
            self._switch_view_mode("full_book")
    
    def _insert_format(self, prefix, suffix):
        """Insert formatting markers around selected text"""
        try:
            selected_text = self.editor_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            replacement = f"{prefix}{selected_text}{suffix}"
            
            self.editor_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.editor_text.insert(tk.INSERT, replacement)
            self.editor_text._apply_text_formatting()
        except tk.TclError:
            # No text selected, insert formatting markers
            if prefix == '# ':
                self.editor_text.insert(tk.INSERT, prefix)
            else:
                self.editor_text.insert(tk.INSERT, prefix + suffix)
                # Position cursor between markers
                cursor_pos = self.editor_text.index(tk.INSERT)
                self.editor_text.mark_set(tk.INSERT, f"{cursor_pos}-{len(suffix)}c")
    
    def _open_epub(self):
        """Open an EPUB file for editing"""
        file_path = filedialog.askopenfilename(
            title="Open EPUB File",
            filetypes=[("EPUB files", "*.epub"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self._load_epub_file(file_path)
                self._update_status(f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open EPUB file:\n{str(e)}")
                self._update_status("Error opening file")
    
    def _load_epub_file(self, file_path):
        """Load and parse an EPUB file"""
        self.current_book = epub.read_epub(file_path)
        self.current_book_path = file_path
        
        # Extract metadata
        title = "Unknown Title"
        author = "Unknown Author"
        
        if self.current_book.get_metadata('DC', 'title'):
            title = self.current_book.get_metadata('DC', 'title')[0][0]
        if self.current_book.get_metadata('DC', 'creator'):
            author = self.current_book.get_metadata('DC', 'creator')[0][0]
        
        # Update interface
        self.book_title_label.config(text=title)
        self.book_author_label.config(text=author)
        
        # Extract chapters
        self.chapters = []
        self.chapter_listbox.delete(0, tk.END)
        
        for item in self.current_book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                chapter_title = soup.find('title')
                if chapter_title:
                    title = chapter_title.get_text().strip()
                else:
                    title = f"Chapter {len(self.chapters) + 1}"
                
                self.chapters.append({
                    'item': item,
                    'title': title,
                    'content': soup.get_text()
                })
                
                self.chapter_listbox.insert(tk.END, title)
        
        self.chapter_count_label.config(text=str(len(self.chapters)))
        
        # Load initial content
        if self.chapters:
            self.current_chapter_index = 0
            self.chapter_listbox.selection_set(0)
            if self.view_mode == "chapter":
                self._load_chapter(0)
            else:
                self._load_full_book()
        
        # Update window title
        self.root.title(f"EPUB Editor - {os.path.basename(file_path)}")
    
    def _load_chapter(self, index):
        """Load a specific chapter into the editor"""
        if 0 <= index < len(self.chapters):
            chapter = self.chapters[index]
            item = chapter['item']
            
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            content = self._html_to_markdown(soup)
            
            self.editor_text.delete(1.0, tk.END)
            self.editor_text.insert(1.0, content)
            self.editor_text._apply_text_formatting()
            
            self._update_status(f"Loaded chapter: {chapter['title']}")
    
    def _load_full_book(self):
        """Load the entire book content into the editor"""
        if not self.chapters:
            return
            
        full_content = ""
        
        for chapter in self.chapters:
            item = chapter['item']
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            
            # Add chapter separator
            full_content += f"=== {chapter['title']} ===\n\n"
            
            # Convert HTML to markdown
            content = self._html_to_markdown(soup)
            full_content += content + "\n\n"
        
        self.editor_text.delete(1.0, tk.END)
        self.editor_text.insert(1.0, full_content.strip())
        self.editor_text._apply_text_formatting()
        
        self._update_status(f"Loaded full book ({len(self.chapters)} chapters)")
    
    def _html_to_markdown(self, soup):
        """Convert HTML content to markdown format"""
        content = ""
        
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'b', 'em', 'i', 'u']):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                content += "#" * level + " " + element.get_text().strip() + "\n\n"
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    content += text + "\n\n"
            elif element.name in ['strong', 'b']:
                content += "**" + element.get_text().strip() + "**"
            elif element.name in ['em', 'i']:
                content += "*" + element.get_text().strip() + "*"
            elif element.name == 'u':
                content += "__" + element.get_text().strip() + "__"
        
        return content.strip()
    
    def _markdown_to_html(self, text):
        """Convert markdown format back to HTML"""
        # Convert headings
        text = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Convert formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'__(.+?)__', r'<u>\1</u>', text)
        
        # Convert paragraphs
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<h'):
                html_paragraphs.append(f'<p>{p}</p>')
            elif p:
                html_paragraphs.append(p)
        
        return '\n'.join(html_paragraphs)
    
    def _on_chapter_selected(self, event):
        """Handle chapter selection from the list"""
        if self.view_mode == "chapter":
            selection = self.chapter_listbox.curselection()
            if selection:
                self.current_chapter_index = selection[0]
                self._load_chapter(self.current_chapter_index)
    
    def _save_epub(self):
        """Save the current EPUB file"""
        if self.current_book_path:
            self._save_epub_to_path(self.current_book_path)
        else:
            self._save_epub_as()
    
    def _save_epub_as(self):
        """Save the EPUB file with a new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save EPUB As",
            defaultextension=".epub",
            filetypes=[("EPUB files", "*.epub"), ("All files", "*.*")]
        )
        
        if file_path:
            self._save_epub_to_path(file_path)
    
    def _save_epub_to_path(self, file_path):
        """Save EPUB content to the specified path"""
        try:
            if self.view_mode == "chapter":
                # Save single chapter
                if self.chapters and 0 <= self.current_chapter_index < len(self.chapters):
                    chapter = self.chapters[self.current_chapter_index]
                    item = chapter['item']
                    
                    content = self.editor_text.get(1.0, tk.END).strip()
                    html_content = self._markdown_to_html(content)
                    
                    full_html = f"""
                    <html>
                    <head>
                        <title>{chapter['title']}</title>
                    </head>
                    <body>
                        {html_content}
                    </body>
                    </html>
                    """
                    
                    item.set_content(full_html.encode('utf-8'))
            else:
                # Save full book
                content = self.editor_text.get(1.0, tk.END).strip()
                chapter_sections = re.split(r'^=== (.+?) ===$', content, flags=re.MULTILINE)
                
                chapter_index = 0
                for i in range(1, len(chapter_sections), 2):
                    if chapter_index < len(self.chapters):
                        chapter = self.chapters[chapter_index]
                        item = chapter['item']
                        
                        chapter_content = chapter_sections[i+1].strip() if i+1 < len(chapter_sections) else ""
                        html_content = self._markdown_to_html(chapter_content)
                        
                        full_html = f"""
                        <html>
                        <head>
                            <title>{chapter['title']}</title>
                        </head>
                        <body>
                            {html_content}
                        </body>
                        </html>
                        """
                        
                        item.set_content(full_html.encode('utf-8'))
                        chapter_index += 1
            
            epub.write_epub(file_path, self.current_book)
            messagebox.showinfo("Success", "EPUB saved successfully!")
            self._update_status(f"Saved: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save EPUB:\n{str(e)}")
            self._update_status("Error saving file")
    
    def _previous_chapter(self):
        """Navigate to the previous chapter"""
        if self.view_mode == "chapter" and self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            self.chapter_listbox.selection_clear(0, tk.END)
            self.chapter_listbox.selection_set(self.current_chapter_index)
            self._load_chapter(self.current_chapter_index)
    
    def _next_chapter(self):
        """Navigate to the next chapter"""
        if self.view_mode == "chapter" and self.current_chapter_index < len(self.chapters) - 1:
            self.current_chapter_index += 1
            self.chapter_listbox.selection_clear(0, tk.END)
            self.chapter_listbox.selection_set(self.current_chapter_index)
            self._load_chapter(self.current_chapter_index)
    
    def _toggle_chapter_panel(self):
        """Show or hide the chapter navigation panel"""
        if self.left_panel.winfo_viewable():
            self.left_panel.pack_forget()
            self._update_status("Chapter panel hidden")
        else:
            self.left_panel.pack(fill=tk.BOTH, expand=True)
            self._update_status("Chapter panel shown")
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
    
    def _undo(self):
        """Undo the last action in the editor"""
        try:
            self.editor_text.edit_undo()
        except tk.TclError:
            pass
    
    def _redo(self):
        """Redo the last undone action"""
        try:
            self.editor_text.edit_redo()
        except tk.TclError:
            pass
    
    def _find_text(self):
        """Open find dialog (placeholder)"""
        messagebox.showinfo("Find", "Find functionality will be implemented in a future version.")
    
    def _replace_text(self):
        """Open replace dialog (placeholder)"""
        messagebox.showinfo("Replace", "Replace functionality will be implemented in a future version.")
    
    def _show_about(self):
        """Display the about dialog"""
        messagebox.showinfo("About EPUB Editor", 
                           "EPUB Editor v1.0\n\n"
                           "A professional EPUB editing application built with Python.\n\n"
                           "Features:\n"
                           "• Open and edit EPUB files\n"
                           "• Chapter and full book view modes\n"
                           "• Rich text formatting with markdown syntax\n"
                           "• Professional Windows-style interface\n\n"
                           "Built with Python and tkinter")
    
    def _update_status(self, message):
        """Update the status bar with a message"""
        self.status_label.config(text=message)

def main():
    """Launch the EPUB editor application"""
    root = tk.Tk()
    app = EpubEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main() 