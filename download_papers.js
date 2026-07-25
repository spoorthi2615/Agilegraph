const https = require('https');
const fs = require('fs');
const path = require('path');

const outDir = path.join(__dirname, 'papers');
if (!fs.existsSync(outDir)){
    fs.mkdirSync(outDir);
}

const downloads = [
    { url: "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf", file: "NIST.FIPS.203.pdf" },
    { url: "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf", file: "NIST.FIPS.204.pdf" },
    { url: "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf", file: "NIST.FIPS.205.pdf" },
    { url: "https://arxiv.org/pdf/2307.06520.pdf", file: "Hasan_Framework_Migrating_PQC.pdf" },
    { url: "https://eprint.iacr.org/2023/487.pdf", file: "Alnahawi_State_of_Crypto_Agility.pdf" },
    { url: "https://arxiv.org/pdf/2404.12854.pdf", file: "Nather_Migrating_Software_PQC.pdf" },
    { url: "https://arxiv.org/pdf/2105.14491.pdf", file: "Brody_GATv2.pdf" },
    { url: "https://arxiv.org/pdf/2604.00560.pdf", file: "Shaw_Quantum_Safe_Code_Auditing.pdf" },
    { url: "https://arxiv.org/pdf/1903.03894.pdf", file: "Ying_GNNExplainer.pdf" },
    { url: "https://eprint.iacr.org/2015/1075.pdf", file: "Mosca_Cybersecurity_Quantum_Computers.pdf" }
];

function downloadFile(url, dest) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(dest);
        https.get(url, (response) => {
            if (response.statusCode === 301 || response.statusCode === 302) {
                return downloadFile(response.headers.location, dest).then(resolve).catch(reject);
            }
            if (response.statusCode !== 200) {
                reject(new Error(`Failed to get '${url}' (${response.statusCode})`));
                return;
            }
            response.pipe(file);
            file.on('finish', () => {
                file.close(resolve);
            });
        }).on('error', (err) => {
            fs.unlink(dest, () => {});
            reject(err);
        });
    });
}

async function run() {
    for (const item of downloads) {
        const dest = path.join(outDir, item.file);
        console.log(`Downloading ${item.file} from ${item.url}...`);
        try {
            await downloadFile(item.url, dest);
            console.log(`Success!`);
        } catch (e) {
            console.error(`Error downloading ${item.file}:`, e.message);
        }
    }
    console.log("All downloads completed.");
}

run();
