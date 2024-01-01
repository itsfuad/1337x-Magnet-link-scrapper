import { parse } from 'node-html-parser';
import { writeFileSync } from 'fs';
//read user input from console
import { createInterface } from 'readline';

const url = "https://1337x.to";

async function getTorrents(query: string){

    console.log(`Searching for ${query}...`);
    //get magnet links from 1337x.to
    const res = await fetch(url + "/search/" + query + "/1/");
    console.log("Parsing data...");
    const html = await res.text();
    const doc = parse(html);


    const torrents: any[] = [];

    const rows = doc.querySelectorAll("tbody > tr");

    for (const row of rows) {

        const item = row.querySelectorAll(".coll-1 > a")[1];
        const name = item?.innerText;
        const torrent = item?.getAttribute("href");
        const seeds = row.querySelector(".coll-2")?.innerText;
        const leeches = row.querySelector(".coll-3")?.innerText;
        const size = row.querySelector(".coll-4")?.innerText;

        if (item){
            torrents.push({
                name,
                torrent,
                seeds,
                leeches,
                size,
            });
        }
    }

    console.log("Getting magnet links...");

    //use promise.All to get magnet links from each torrent asynchronously
    const promises = torrents.map(async (torrent) => {
        torrent.magnet = await getMagnet(torrent.torrent);
        delete torrent.torrent;
    });

    await Promise.all(promises);

    console.log("Writing to csv file...");

    //convert array of objects csv file
    let csv = torrents.map((torrent) => {
        return Object.values(torrent).join(",");
    }).join("\n");

    //append header to csv file
    const header = Object.keys(torrents[0]).join(",");
    csv = header + "\n" + csv;

    //write csv file to disk

    writeFileSync("torrents.csv", csv);

    console.log("Done");
}

const magnetRegex = /magnet:([^"]+)/g;

async function getMagnet(torrent: string){
    //get magnet link from 1337x.to
    //console.log(`Getting magnet for ${url + torrent}`);
    const res = await fetch(url + torrent);
    const html = await res.text();
    //parse html to get magnet link
    const magnet = html.match(magnetRegex)?.[0] || "";

    return magnet;
}

//ask user for search query

const query = await new Promise<string>((resolve) => {
    const rl = createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    rl.question("Enter search query: ", (answer) => {
        rl.close();
        resolve(answer);
    });
});

getTorrents(query);