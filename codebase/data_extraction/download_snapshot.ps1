# ———————————————————————————————————————————————————————————————————————————————————————————— #
# This PowerShell script is designed to download snapshots of liquidity data                   #
# from the Uniswap V3 protocol and options book summaries from the Deribit exchange.           #
# It interacts with The Graph's API to fetch data related to specific Uniswap V3               #
# pools (ETH/USDC with 5bp and 30bp fee tiers) and saves the retrieved information             #   
# in JSON format in designated directories. The script also retrieves a summary of the options #
# book for ETH from Deribit and saves it similarly.                                            #        
# ———————————————————————————————————————————————————————————————————————————————————————————— #


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Local paths and output directories
$PROJECT_ROOT = Resolve-Path "$PSScriptRoot\..\..\.." | Select-Object -ExpandProperty Path
Set-Location -Path $PROJECT_ROOT
# Output directories for raw data
$LIQ_DIR = Join-Path $PROJECT_ROOT "data\raw\liquidity"
$OPTS_DIR = Join-Path $PROJECT_ROOT "data\raw\options"
New-Item -ItemType Directory -Force -Path $LIQ_DIR  | Out-Null
New-Item -ItemType Directory -Force -Path $OPTS_DIR | Out-Null


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# API details and parameters
$API_KEY = $env:GRAPH_API_KEY
if (-not $API_KEY) { throw "Set the GRAPH_API_KEY environment variable before running this script." }
# Uniswap V3 subgraph details -> Mainnet, hosted service
$SUBGRAPH_ID = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
$ENDPOINT = "https://gateway.thegraph.com/api/$API_KEY/subgraphs/id/$SUBGRAPH_ID"
# Uniswap V3 pool addresses (lowercase, no checksum) -> ETH/USDC 5bp and 30bp fee tiers
$POOL_5BP = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
$POOL_30BP = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"

# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Data extraction - liquidity snapshots

# Pool state
foreach ($POOL in @($POOL_5BP, $POOL_30BP)) {
    $TAG = if ($POOL -eq $POOL_5BP) { "5bp" } else { "30bp" }

    $query = '{"query":"{ pool(id: \"' + $POOL + '\") { sqrtPrice tick liquidity token0Price token1Price } }"}'

    $OUT = Join-Path $LIQ_DIR "eth_usdc_${TAG}_pool_state.json"
    Invoke-RestMethod -Uri $ENDPOINT -Method Post -ContentType "application/json" -Body $query |
    ConvertTo-Json -Depth 10 | Out-File $OUT -Encoding utf8
    Write-Host "Downloaded pool state: $TAG -> $OUT"
}

foreach ($POOL in @($POOL_5BP, $POOL_30BP)) {
    $TAG = if ($POOL -eq $POOL_5BP) { "5bp" } else { "30bp" }
    $PAGE = 0
    $CURSOR = -887272

    while ($true) {
        $query = '{"query":"{ ticks(first: 1000, where: {pool: \"' + $POOL + '\", tickIdx_gt: ' + $CURSOR + '}, orderBy: tickIdx, orderDirection: asc) { tickIdx liquidityNet liquidityGross } }"}'

        $RESULT = Invoke-RestMethod -Uri $ENDPOINT -Method Post -ContentType "application/json" -Body $query
        $OUT = J#oin-Path $LIQ_DIR "eth_usdc_${TAG}_ticks_page${PAGE}.json"
        $RESULT | ConvertTo-Json -Depth 10 | Out-File $OUT -Encoding utf8

        $TICKS = $RESULT.data.ticks
        $COUNT = $TICKS.Count
        Write-Host "  $TAG page ${PAGE}: $COUNT ticks"

        if ($COUNT -lt 1000) { break }

        $CURSOR = $TICKS[$COUNT - 1].tickIdx
        $PAGE++
        Start-Sleep -Milliseconds 500
    }
}

# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Data extraction - options book summary
$TS = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$OUT = Join-Path $OPTS_DIR "${TS}_eth_options_book_summary.json"
Invoke-RestMethod -Uri "https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=ETH&kind=option" |
ConvertTo-Json -Depth 10 | Out-File $OUT -Encoding utf8
Write-Host "Downloaded options book summary -> $OUT"
