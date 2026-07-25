$outDir = "d:\projects\major project\cryptograph\papers"
New-Item -ItemType Directory -Force -Path $outDir

$downloads = @(
    @{ Url = "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf"; File = "NIST.FIPS.203.pdf" },
    @{ Url = "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf"; File = "NIST.FIPS.204.pdf" },
    @{ Url = "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf"; File = "NIST.FIPS.205.pdf" },
    @{ Url = "https://arxiv.org/pdf/2307.06520"; File = "Hasan_Framework_Migrating_PQC.pdf" },
    @{ Url = "https://eprint.iacr.org/2023/487.pdf"; File = "Alnahawi_State_of_Crypto_Agility.pdf" },
    @{ Url = "https://arxiv.org/pdf/2404.12854"; File = "Nather_Migrating_Software_PQC.pdf" },
    @{ Url = "https://arxiv.org/pdf/2105.14491"; File = "Brody_GATv2.pdf" },
    @{ Url = "https://arxiv.org/pdf/2604.00560"; File = "Shaw_Quantum_Safe_Code_Auditing.pdf" },
    @{ Url = "https://arxiv.org/pdf/1903.03894"; File = "Ying_GNNExplainer.pdf" },
    @{ Url = "https://eprint.iacr.org/2015/1075.pdf"; File = "Mosca_Cybersecurity_Quantum_Computers.pdf" }
)

foreach ($item in $downloads) {
    $outFile = Join-Path $outDir $item.File
    Write-Host "Downloading $($item.File) from $($item.Url)..."
    try {
        Invoke-WebRequest -Uri $item.Url -OutFile $outFile
        Write-Host "Success!"
    } catch {
        Write-Host "Failed to download $($item.Url): $_"
    }
}

Write-Host "Finished downloading papers to $outDir"
