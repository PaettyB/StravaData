'use strict';

const fetch = require("node-fetch");

const PORT = 45976

const publicActivities = ["Ride", "Run", "Walk", "Swim", "Hike"];

const fs = require("fs")
const tokenFile = "tokens.json";
var tokens = JSON.parse(fs.readFileSync(tokenFile));
var credentials = JSON.parse(fs.readFileSync("credentials.json"))

listActivities(1, 200);

async function listActivities(page, per_page) {
  const accessToken = await getAccessToken();
  const list = await fetch('https://www.strava.com/api/v3/athlete/activities' + "?page=" + page  + "&per_page=" + per_page, {
    method: 'GET',
    headers:{
      'accept': 'application/json',
      'authorization': "Bearer " + accessToken
    },
  }).then(res => res.json());
  fs.writeFileSync("activities.json", JSON.stringify(list));
}

async function handleUpload(id) {
  const accessToken = await getAccessToken(); 
  const activity = await getActivity(accessToken, id);
  if(!activity.type) {
    console.log("Could not get Activity ", activity);
    return;
  }
  console.log(activity.type);
  // if(publicActivities.includes(activity.type)) return;
  const resp = await setPrivate(accessToken, id);
  // const resp = await setName(accessToken, id);
  console.log(resp);
}

async function getAccessToken() {
  if(tokens.expires_at < (Date.now() / 1000)){
    // refreshToken
    console.log("Token expired.");
    const tokenResponse = await refreshTokens();
    if(!tokenResponse.access_token) {
      console.error("Failed to fetch new tokens");
      return null;
    }
    console.log(tokenResponse);
    tokens.access_token = tokenResponse.access_token;
    tokens.refresh_token = tokenResponse.refresh_token;
    tokens.expires_at = tokenResponse.expires_at;
    fs.writeFileSync(tokenFile, JSON.stringify(tokens, null, 2));
    console.log("Using newly generated token " + tokens.access_token);
    return tokens.access_token;
  } else {
    console.log("Using Access Token " + tokens.access_token);
    return  tokens.access_token;
  }
}

async function refreshTokens() {
  return fetch('https://www.strava.com/oauth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      client_id: credentials.client_id,
      client_secret: credentials.client_secret,
      grant_type: "refresh_token",
      refresh_token: tokens.refresh_token
    })
  }).then(res => res.json());
}

async function getActivity(accessToken, id){
  return fetch('https://www.strava.com/api/v3/activities/' + id + "?include_all_efforts=false", {
    method: 'GET',
    headers:{
      'accept': 'application/json',
      'authorization': "Bearer " + accessToken
    },
  }).then(res => res.json());
}




async function setName(accessToken, id) {
  return fetch('https://www.strava.com/api/v3/activities/' + id, {
    method: 'PUT',
    headers:{
      'Accept': 'application/json',
      'Authorization': "Bearer " + accessToken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: "Leichter Lauf am Sonntag"
    }
    )
  }).then(res => res.json());
}


// DOES NOT WORK
// async function setPrivate(accessToken, id) {
//   return fetch('https://www.strava.com/api/v3/activities/' + id, {
//     method: 'PUT',
//     headers:{
//       'Accept': 'application/json',
//       'Authorization': "Bearer " + accessToken,
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({
//       private: "true",
//       visibility: "only_me"
//     })
//   }).then(res => res.json());
// }