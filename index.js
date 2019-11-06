const boxrec = require("boxrec").Boxrec;
const fastcsv = require('fast-csv');
const fs = require('fs');
async function getCookieJar(){
    try {
        const cookieJar = await boxrec.login('oldkingthor','K@leidoscope69');
        return cookieJar;
    } catch (e) {
        console.log("Login error: " + e);
    }
};
async function writeData() {
    const cookieJar = await getCookieJar();
    var boxers = await boxrec.getPeopleByName(cookieJar,"Deontay","Wilder");
    console.log(boxers.output);
};
try {
    writeData();
} catch (error) {
    console.log("Error in writeData: " + error);
}
