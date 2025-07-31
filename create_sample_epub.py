#!/usr/bin/env python3
"""
Sample EPUB Creator
Creates a sample EPUB file for testing the EPUB Editor.
"""

import os
from ebooklib import epub

def create_sample_epub():
    """Create a sample EPUB file for testing"""
    
    # Create the book
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier('sample-epub-123')
    book.set_title('Sample Book')
    book.set_language('en')
    book.add_author('Sample Author')
    
    # Create chapters
    chapters = []
    
    # Chapter 1
    chapter1_content = '''
    <html>
    <head>
        <title>Chapter 1: Introduction</title>
    </head>
    <body>
        <h1>Chapter 1: Introduction</h1>
        <p>This is the first chapter of our sample book. It introduces the reader to the world of EPUB editing.</p>
        <p>EPUB files are a popular format for digital books, and this editor allows you to modify their content easily.</p>
        <h2>What is EPUB?</h2>
        <p>EPUB (Electronic Publication) is a free and open e-book standard by the International Digital Publishing Forum (IDPF).</p>
        <p>It's designed for reflowable content, meaning the text display can be optimized for the particular display device used by the reader.</p>
    </body>
    </html>
    '''
    
    chapter1 = epub.EpubHtml(title='Chapter 1: Introduction', 
                            file_name='chapter1.xhtml',
                            content=chapter1_content)
    book.add_item(chapter1)
    chapters.append(chapter1)
    
    # Chapter 2
    chapter2_content = '''
    <html>
    <head>
        <title>Chapter 2: Getting Started</title>
    </head>
    <body>
        <h1>Chapter 2: Getting Started</h1>
        <p>In this chapter, we'll explore how to use the EPUB Editor effectively.</p>
        <p>The editor provides several key features:</p>
        <ul>
            <li>Open and edit EPUB files</li>
            <li>Navigate between chapters</li>
            <li>Live preview of changes</li>
            <li>Basic text formatting</li>
        </ul>
        <h2>Basic Workflow</h2>
        <p>1. Open an EPUB file using File → Open EPUB...</p>
        <p>2. Select a chapter from the left panel</p>
        <p>3. Edit the content in the editor panel</p>
        <p>4. Preview your changes in the preview panel</p>
        <p>5. Save your work using File → Save</p>
    </body>
    </html>
    '''
    
    chapter2 = epub.EpubHtml(title='Chapter 2: Getting Started', 
                            file_name='chapter2.xhtml',
                            content=chapter2_content)
    book.add_item(chapter2)
    chapters.append(chapter2)
    
    # Chapter 3
    chapter3_content = '''
    <html>
    <head>
        <title>Chapter 3: Advanced Features</title>
    </head>
    <body>
        <h1>Chapter 3: Advanced Features</h1>
        <p>This chapter covers some of the more advanced features of the EPUB Editor.</p>
        <h2>View Modes</h2>
        <p>The editor supports multiple view modes:</p>
        <ul>
            <li><strong>Preview:</strong> Shows formatted text as it would appear in an EPUB reader</li>
            <li><strong>Source:</strong> Shows only the editor (no preview)</li>
            <li><strong>Split:</strong> Shows both editor and preview side by side</li>
        </ul>
        <h2>Text Formatting</h2>
        <p>You can apply basic formatting to your text:</p>
        <p><strong>Bold text</strong> for emphasis</p>
        <p><em>Italic text</em> for titles or foreign words</p>
        <p><u>Underlined text</u> for important points</p>
        <h2>Keyboard Shortcuts</h2>
        <p>Use keyboard shortcuts for faster editing:</p>
        <ul>
            <li>Ctrl+O: Open EPUB file</li>
            <li>Ctrl+S: Save EPUB file</li>
            <li>Ctrl+Z: Undo</li>
            <li>Ctrl+Y: Redo</li>
            <li>F11: Toggle fullscreen</li>
        </ul>
    </body>
    </html>
    '''
    
    chapter3 = epub.EpubHtml(title='Chapter 3: Advanced Features', 
                            file_name='chapter3.xhtml',
                            content=chapter3_content)
    book.add_item(chapter3)
    chapters.append(chapter3)
    
    # Create table of contents
    book.toc = [(epub.Section('Sample Book'), chapters)]
    
    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        margin: 2em;
    }
    h1 {
        color: #333;
        border-bottom: 2px solid #333;
        padding-bottom: 0.5em;
    }
    h2 {
        color: #555;
        margin-top: 1.5em;
    }
    ul {
        margin-left: 2em;
    }
    li {
        margin-bottom: 0.5em;
    }
    '''
    
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    
    # Create spine
    book.spine = ['nav'] + chapters
    
    # Write EPUB file
    epub_path = 'sample_book.epub'
    epub.write_epub(epub_path, book)
    
    print(f"Sample EPUB created: {epub_path}")
    print("You can now open this file in the EPUB Editor to test the functionality.")
    
    return epub_path

if __name__ == "__main__":
    create_sample_epub() 