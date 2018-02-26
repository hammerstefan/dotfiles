
function! BufCloseOthers()
    let l:curfile = @%
    bufdo! Bclose
    execute "edit " . l:curfile
endfunction

command BCloseOthers :call BufCloseOthers()
