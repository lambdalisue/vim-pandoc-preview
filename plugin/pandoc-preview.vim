" Ref: https://github.com/mattn/mkdpreview-vim/blob/master/plugin/mkdpreview.vim
let s:pyscript = expand('<sfile>:p:h:h') . '/lib/viewer.py'

if !exists("g:pandoc_command") || !g:pandoc_command
  let g:pandoc_command = "pandoc -Ss --toc -t html"
endif
if !exists("g:pandoc_preview_host") || !g:pandoc_preview_host
  let g:pandoc_preview_host = "localhost"
endif
if !exists("g:pandoc_preview_port") || !g:pandoc_preview_port
  let g:pandoc_preview_port = "8081"
endif

function! s:update_preview()
  let l:url = printf("http://%s:%s/", 
    \ g:pandoc_preview_host,
    \ g:pandoc_preview_port)
  let ret = webapi#http#post(l:url, {
    \ "filename" : expand("%:p")
    \})
  if exists("g:pandoc_preview_debug") && g:pandoc_preview_debug
    echo ret.content
  endif
endfunction

function! s:preview(bang)
  if a:bang == '!'
    let l:command = printf("%s -c %s -o %s -p %s",
      \ shellescape(s:pyscript),
      \ shellescape(g:pandoc_command),
      \ shellescape(g:pandoc_preview_host),
      \ shellescape(g:pandoc_preview_port))
    if has('win32') || has('win64')
      if exists('g:pandoc_preview_python_path')
        silent exe printf("!start %s %s",
          \ shellescape(g:pandoc_preview_python_path),
          \ l:command)
      else
        silent exe "!start pythonw ".shellescape(l:command)
      endif
    else
      if exists('g:pandoc_preview_python_path')
        call system(printf("%s %s & 2>&1 /dev/null",
          \ shellescape(g:pandoc_preview_python_path),
          \ l:command))
      else
        call system(printf("%s & 2>&1 /dev/null", l:command))
      endif
    endif
    sleep 1
    " FIXME: On MacOSX system() above return v:shell_error 7.
    "if v:shell_error != 0 && ((has('win32') || has('win64')) && v:shell_error != 52)
    "  echohl ErrorMsg | echomsg "fail to start 'viewer.py'" | echohl None
    "  return
    "endif
    augroup Preview
      autocmd!
      autocmd BufWritePost <buffer> call <SID>update_preview()
    augroup END
  endif
  call s:update_preview()
endfunction

command! -bang PandocPreview call <SID>preview('<bang>')
