**See [shareboard.vim](https://github.com/lambdalisue/shareboard.vim) which I newly made. It is more flexible and useful :-)**

% vim-pandoc-preview README
% lambdalisue <lambdalisue@hashnote.net>
% 2012.12.13

[Pandoc] viewer for Vimmer. Inspired by [MkdPreview]


Introduction
=============================================================================

Vim can't dispaly characters which have them glyphs for each like web browser.
So unfortunately, vimmer can't preview markdown text over editing on terminal.
This is a GUI application which can display preview of markup laungages which
[Pandoc] supports.



Installation
=============================================================================

Copy or git-clone `vim-pandoc-preview` into your `~/.vim/bundle`.

    # cd /path/to/your/.vimrc/bundle
    # git clone https://github.com/lambdalisue/vim-pandoc-preview

This require following third party modules or vim plugins.

* [Pandoc]
* [Python] (2.7 or later)
* [PyQt4]
* [curl] command
* [webapi-vim]


Usage
=============================================================================

    :PandocPreview!

If you have previewer already, Just type:

    :PandocPreview

`:PandocPreview!` command install `BufWritePost` hook for current buffer.
Then preview will be updated just to do `:w`.


Author
=============================================================================

Alisue<lambdalisue@hashnote.net>

[Python]: http://python.org
[PyQt4]:  http://www.riverbankcomputing.co.uk/software/pyqt/download>
[MkdPreview]: https://github.com/mattn/mkdpreview-vim
[Pandoc]: http://johnmacfarlane.net/pandoc/index.html 
[curl]: http://curl.haxx.se/libcurl/
[webapi-vim]: http://github.com/mattn/webapi-vim
