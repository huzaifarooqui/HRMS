param([Parameter(Mandatory=$true)][string]$WorkbookPath)
$ErrorActionPreference="Stop";$excel=$null;$book=$null;$sheet=$null
try {
 $excel=New-Object -ComObject Excel.Application;$excel.Visible=$false;$excel.DisplayAlerts=$false;$excel.AskToUpdateLinks=$false;$excel.EnableEvents=$false
 $book=$excel.Workbooks.Open($WorkbookPath,0,$true)
 foreach($ws in $book.Worksheets){if($ws.Name -eq "Performance"){$sheet=$ws;break}}
 if($null -eq $sheet){throw "Performance sheet not found."}
 if($sheet.PivotTables().Count -lt 3){throw "Expected 3 PivotTables on Performance sheet."}
 $tables=@()
 for($pi=1;$pi -le 3;$pi++){
   $pivot=$sheet.PivotTables().Item($pi);$range=$pivot.TableRange2
   $top=[int]$range.Row;$left=[int]$range.Column;$rc=[int]$range.Rows.Count;$cc=[int]$range.Columns.Count
   # DRR is a virtual worksheet column immediately to the right of each PivotTable.
   # PivotTable layouts do not all place their real header on the same relative row,
   # so search the first few rows beside the Pivot instead of assuming top+1.
   $hasDrr=$false
   $probeMax=[Math]::Min(4,$rc)
   for($probe=0;$probe -lt $probeMax;$probe++){
     $adj=[string]$sheet.Cells.Item($top+$probe,$left+$cc).Text
     if($adj.Trim().ToUpper() -eq 'DRR'){$hasDrr=$true;break}
   }
   if($hasDrr){$cc++}
   $rr=$sheet.Range($sheet.Cells.Item($top,$left),$sheet.Cells.Item($top+$rc-1,$left+$cc-1))
   $rows=@();for($r=1;$r -le $rr.Rows.Count;$r++){$cells=@();for($c=1;$c -le $rr.Columns.Count;$c++){$cells += [string]$rr.Cells.Item($r,$c).Text};$rows += ,@($cells)}
   $tables += [PSCustomObject]@{index=$pi;name=[string]$pivot.Name;rows=$rows}
   [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($rr);[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($range);[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pivot)
 }
 [PSCustomObject]@{sheet='Performance';tables=$tables}|ConvertTo-Json -Compress -Depth 12
} finally {
 if($null -ne $book){try{$book.Close($false)}catch{}};if($null -ne $excel){try{$excel.Quit()}catch{}}
 foreach($o in @($sheet,$book,$excel)){if($null -ne $o){try{[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($o)}catch{}}};[GC]::Collect();[GC]::WaitForPendingFinalizers()
}