param(
    [Parameter(Mandatory=$true)][string]$WorkbookPath
)

$ErrorActionPreference = "Stop"
$excel = $null
$book = $null
$sheet = $null
$pivot = $null
$range = $null
$readRange = $null

try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AskToUpdateLinks = $false
    $excel.EnableEvents = $false

    # Read-only. No refresh, edit, calculate or save.
    $book = $excel.Workbooks.Open($WorkbookPath, 0, $true)

    foreach ($ws in $book.Worksheets) {
        if ($ws.Name -eq "Performance") {
            $sheet = $ws
            break
        }
    }
    if ($null -eq $sheet) { throw "Performance sheet not found." }

    if ($sheet.PivotTables().Count -lt 1) {
        throw "No PivotTable found on Performance sheet."
    }

    $pivot = $sheet.PivotTables().Item(1)
    $range = $pivot.TableRange2

    $topRow = [int]$range.Row
    $leftCol = [int]$range.Column
    $rowCount = [int]$range.Rows.Count
    $colCount = [int]$range.Columns.Count

    # Some workbooks keep DRR as a formula/display column immediately beside the Pivot.
    # Include it ONLY if the visible header next to the Pivot says DRR.
    $headerRow = $topRow + 1
    $rightHeader = [string]$sheet.Cells.Item($headerRow, $leftCol + $colCount).Text
    if ($rightHeader.Trim().ToUpper() -eq "DRR") {
        $colCount = $colCount + 1
    }

    $readRange = $sheet.Range(
        $sheet.Cells.Item($topRow, $leftCol),
        $sheet.Cells.Item($topRow + $rowCount - 1, $leftCol + $colCount - 1)
    )

    $rows = @()
    for ($r = 1; $r -le $readRange.Rows.Count; $r++) {
        $cells = @()
        for ($c = 1; $c -le $readRange.Columns.Count; $c++) {
            $cells += [string]$readRange.Cells.Item($r,$c).Text
        }
        $rows += ,@($cells)
    }

    [PSCustomObject]@{
        sheet = "Performance"
        pivot_name = [string]$pivot.Name
        rows = $rows
    } | ConvertTo-Json -Compress -Depth 10
}
finally {
    if ($null -ne $book) { try { $book.Close($false) } catch {} }
    if ($null -ne $excel) { try { $excel.Quit() } catch {} }

    foreach ($obj in @($readRange,$range,$pivot,$sheet,$book,$excel)) {
        if ($null -ne $obj) {
            try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($obj) } catch {}
        }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
