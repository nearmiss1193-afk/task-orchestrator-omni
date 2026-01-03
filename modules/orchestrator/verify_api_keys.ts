
import axios from 'axios';
import * as fs from 'fs';

const LOCATION_ID = 'RnK4OjX0oDcqtWw0VyLr';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6InVGWWNaQTdaazZFY0J6ZTVCNG9IIiwidmVyc2lvbiI6MSwiaWF0IjoxNzY2MTU1NTkxOTI1LCJzdWIiOiJPZEE3MTRrOEJVSU9jWnNCV0VoOCJ9.kfoVgriQUDYZ-uhH9cJWYQsOgsqD8eFsPJXVgsEeDZU';
const PIT_TOKEN = 'pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199';

async function testKey(name: string, token: string, type: 'Bearer') {
    console.log(`\nTesting ${name}...`);
    try {
        // Try V2 Location Endpoint
        const url = `https://services.leadconnectorhq.com/locations/${LOCATION_ID}`;
        const response = await axios.get(url, {
            headers: {
                'Authorization': `${type} ${token}`,
                'Version': '2021-07-28'
            }
        });
        console.log(`[SUCCESS] ${name} accessed Location V2.`);
        console.log('Location Name:', response.data.location?.name || response.data.name);
        return true;
    } catch (e: any) {
        console.log(`[FAIL] ${name} - ${e.message}`);
        if (e.response) {
            console.log('Status:', e.response.status);
            console.log('Data:', JSON.stringify(e.response.data));
        }
        return false;
    }
}

async function run() {
    await testKey('JWT Token', JWT_TOKEN, 'Bearer');
    await testKey('PIT Token', PIT_TOKEN, 'Bearer');
}

run();
