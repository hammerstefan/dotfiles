set expandtab
set tabstop=4
set shiftwidth=4
set guioptions -=m
set guioptions -=T
if has("gui_running")
    colorscheme yaflandia
else
    colorscheme industry
endif

set guifont=DejaVu\ Sans\ Mono\ 8
set undodir=~/.vim/undodir
set undofile


set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

Bundle 'nathanalderson/yang.vim'
Plugin 'mileszs/ack.vim'
Plugin 'scrooloose/nerdtree'
Plugin 'scrooloose/nerdcommenter'
Plugin 'majutsushi/tagbar'
Bundle 'ctrlpvim/ctrlp.vim'
Plugin 'JessicaKMcIntosh/TagmaBufMgr'

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line

let g:loaded_logipat = 1 

if executable('ag')
  let g:ackprg = 'ag --vimgrep'
endif

vmap <silent> <unique> <F4> y:Ack "<c-r>""<CR>
map <F3> :TagbarToggle<CR>

" NERDTree
map <F1> :NERDTreeToggle<CR>
" Use NERDTree if vim is opening directory
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) && !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | endif

" Put plugins and dictionaries in this dir (also on Windows)
let vimDir = '$HOME/.vim'
let &runtimepath.=','.vimDir

" Keep undo history across sessions by storing it in a file
if has('persistent_undo')
    let myUndoDir = expand(vimDir . '/undodir')
    " Create dirs
    call system('mkdir ' . vimDir)
    call system('mkdir ' . myUndoDir)
    let &undodir = myUndoDir
    set undofile
endif

" Add command to set window title elegantly (thanks Ryan Hill)
command -nargs=1 Ctitle set titlestring=<args>\ -\ %{expand('%:p:h')}/%t
