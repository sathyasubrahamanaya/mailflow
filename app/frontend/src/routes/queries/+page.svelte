<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type UserQuery } from '$lib/api';
	import QueryCard from '$lib/components/QueryCard.svelte';
	import { fade, fly } from 'svelte/transition';

	let queries = $state<UserQuery[]>([]);
	let isLoading = $state(true);
	let error = $state('');
	let activeTab = $state<'open' | 'closed'>('open');

	async function fetchQueries() {
		isLoading = true;
		error = '';
		try {
			const res = await api.getQueries();
			if (res.ErrorCode === 0) {
				// The API might return a list of queries in res.Data.queries or res.Data
				queries = res.Data.queries || [];
			} else {
				error = res.Message;
			}
		} catch (err) {
			error = 'Failed to fetch queries';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	onMount(fetchQueries);

	let filteredQueries = $derived(queries.filter((q) => q.status.toLowerCase() === activeTab));

	let stats = $derived({
		open: queries.filter((q) => q.status.toLowerCase() === 'open').length,
		closed: queries.filter((q) => q.status.toLowerCase() === 'closed').length
	});
</script>

<div class="space-y-8">
	<div class="flex flex-col justify-between gap-4 md:flex-row md:items-center">
		<div>
			<h1 class="mb-2 text-3xl font-bold text-gray-900">Support Queries</h1>
			<p class="text-gray-500">Manage and respond to user support requests</p>
		</div>
		<button
			onclick={fetchQueries}
			class="inline-flex items-center rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-all hover:bg-gray-50 active:scale-95"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`}
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
				/>
			</svg>
			Refresh
		</button>
	</div>

	<!-- Stats Grid -->
	<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
		<div
			class="flex items-center space-x-4 rounded-3xl border border-gray-100 bg-white p-6 shadow-sm"
		>
			<div
				class="flex h-12 w-12 items-center justify-center rounded-2xl bg-green-100 text-green-600"
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
						d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
			</div>
			<div>
				<p class="text-sm font-medium tracking-wider text-gray-400 uppercase">Open Queries</p>
				<p class="text-2xl font-bold text-gray-900">{stats.open}</p>
			</div>
		</div>
		<div
			class="flex items-center space-x-4 rounded-3xl border border-gray-100 bg-white p-6 shadow-sm"
		>
			<div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600">
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
						d="M5 13l4 4L19 7"
					/>
				</svg>
			</div>
			<div>
				<p class="text-sm font-medium tracking-wider text-gray-400 uppercase">Resolved Queries</p>
				<p class="text-2xl font-bold text-gray-900">{stats.closed}</p>
			</div>
		</div>
	</div>

	<!-- Tabs & Content -->
	<div class="overflow-hidden rounded-3xl border border-gray-100 bg-white shadow-sm">
		<div class="flex border-b border-gray-100 bg-gray-50/50 p-2">
			<button
				onclick={() => (activeTab = 'open')}
				class={`flex-1 rounded-xl px-4 py-3 text-sm font-bold transition-all ${activeTab === 'open' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:bg-white/50 hover:text-gray-700'}`}
			>
				Open ({stats.open})
			</button>
			<button
				onclick={() => (activeTab = 'closed')}
				class={`flex-1 rounded-xl px-4 py-3 text-sm font-bold transition-all ${activeTab === 'closed' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:bg-white/50 hover:text-gray-700'}`}
			>
				Closed ({stats.closed})
			</button>
		</div>

		<div class="p-6">
			{#if isLoading && queries.length === 0}
				<div class="space-y-4">
					{#each Array(3) as _}
						<div class="h-48 animate-pulse rounded-2xl bg-gray-50"></div>
					{/each}
				</div>
			{:else if error}
				<div class="rounded-2xl border border-red-100 bg-red-50 py-20 text-center">
					<p class="mb-4 font-medium text-red-600">{error}</p>
					<button onclick={fetchQueries} class="font-bold text-red-700 hover:underline"
						>Try Again</button
					>
				</div>
			{:else if filteredQueries.length === 0}
				<div class="py-20 text-center text-gray-400">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="mx-auto mb-4 h-16 w-16 opacity-20"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
						/>
					</svg>
					<p class="text-xl font-medium">No {activeTab} queries found</p>
				</div>
			{:else}
				<div class="space-y-6">
					{#each filteredQueries as query (query.id)}
						<div in:fly={{ y: 20, duration: 300 }}>
							<QueryCard {query} onReply={fetchQueries} />
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
