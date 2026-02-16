import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const initialApiKey = browser ? localStorage.getItem('api_key') : null;

export const apiKey = writable<string | null>(initialApiKey);

if (browser) {
    apiKey.subscribe((value) => {
        if (value) {
            localStorage.setItem('api_key', value);
        } else {
            localStorage.removeItem('api_key');
        }
    });
}

export const isAuthenticated = writable<boolean>(!!initialApiKey);

apiKey.subscribe((value) => {
    isAuthenticated.set(!!value);
});
