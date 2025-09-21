/**
 * Name: main.js
 * Description: Just a simple entry point to mount the Svelte app.
 * Inputs: None
 * Outputs: None
 * External Sources: N/A
 * Author(s): Nicholas Holmes
 * Creation Date: 18 September 2025
 */

import './app.css';
import App from './App.svelte';
import { mount } from 'svelte';

mount(App, { target: document.getElementById('app') });
