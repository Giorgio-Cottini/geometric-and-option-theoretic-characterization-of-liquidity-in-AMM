Get-ChildItem -Path $PSScriptRoot -Recurse -File -Include main.aux,main.bcf,main.bbl,main.blg,main.fdb_latexmk,main.fls,main.log,main.out,main.run.xml,main.synctex.gz,main.toc | Remove-Item -Force
