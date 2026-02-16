<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';
	import { isAuthenticated, apiKey } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let { children } = $props();

	function logout() {
		apiKey.set(null);
		goto('/');
	}

	$effect(() => {
		if (!$isAuthenticated && page.url.pathname !== '/') {
			goto('/');
		} else if ($isAuthenticated && page.url.pathname === '/') {
			goto('/queries');
		}
	});

	let isSidebarOpen = $state(true);
</script>

<div class="flex min-h-screen bg-gray-50">
	{#if $isAuthenticated}
		<!-- Sidebar -->
		<aside
			class="fixed inset-y-0 left-0 z-50 overflow-hidden bg-white shadow-xl transition-all duration-300 {isSidebarOpen
				? 'w-64'
				: 'w-20'}"
		>
			<div class="flex h-full flex-col p-4">
				<div class="mb-8 flex items-center justify-between">
					{#if isSidebarOpen}
						<h1
							class="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-2xl font-bold text-transparent"
						>
							MailFlow Admin
						</h1>
					{/if}
					<button
						onclick={() => (isSidebarOpen = !isSidebarOpen)}
						class="rounded-lg p-2 transition-colors hover:bg-gray-100"
						aria-label={isSidebarOpen ? 'Close sidebar' : 'Open sidebar'}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 6h16M4 12h16M4 18h16"
							/>
						</svg>
					</button>
				</div>

				<nav class="flex-1 space-y-2">
					<a
						href="/queries"
						class="flex items-center rounded-xl p-3 transition-all duration-200 {page.url
							.pathname === '/queries'
							? 'bg-blue-50 text-blue-600 shadow-sm'
							: 'text-gray-600 hover:bg-gray-50'}"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="mr-3 h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586l-4-4A2 2 0 013 10V4a2 2 0 012-2h10a2 2 0 012 2v4M14 4h6m-6 4h6"
							/>
						</svg>
						{#if isSidebarOpen}<span>Queries</span>{/if}
					</a>

					<a
						href="/feedback"
						class="flex items-center rounded-xl p-3 transition-all duration-200 {page.url
							.pathname === '/feedback'
							? 'bg-blue-50 text-blue-600 shadow-sm'
							: 'text-gray-600 hover:bg-gray-50'}"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="mr-3 h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.382-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
							/>
						</svg>
						{#if isSidebarOpen}<span>Feedback</span>{/if}
					</a>
				</nav>

				<button
					onclick={logout}
					class="mt-auto flex items-center rounded-xl p-3 text-red-600 transition-all duration-200 hover:bg-red-50"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="mr-3 h-6 w-6"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
						/>
					</svg>
					{#if isSidebarOpen}<span>Logout</span>{/if}
				</button>
			</div>
		</aside>

		<!-- Main content -->
		<main class="flex-1 transition-all duration-300 {isSidebarOpen ? 'ml-64' : 'ml-20'}">
			<div class="mx-auto max-w-7xl p-8">
				{@render children()}
			</div>
		</main>
	{:else}
		<main class="flex-1">
			{@render children()}
		</main>
	{/if}
</div>

<style>
	:global(body) {
		font-family:
			'Inter',
			system-ui,
			-apple-system,
			sans-serif;
	}
	:global(body) {
		background-color: rgb(249 250 251);
		color: rgb(17 24 39);
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}
</style>
