<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Feedback } from '$lib/api';
	import FeedbackCard from '$lib/components/FeedbackCard.svelte';
	import { fly } from 'svelte/transition';

	let feedbacks = $state<Feedback[]>([]);
	let isLoading = $state(true);
	let error = $state('');

	async function fetchFeedbacks() {
		isLoading = true;
		error = '';
		try {
			const res = await api.getFeedbacks();
			if (res.ErrorCode === 0) {
				feedbacks = res.Data.feedbacks || [];
			} else {
				error = res.Message;
			}
		} catch (err) {
			error = 'Failed to fetch feedback';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	onMount(fetchFeedbacks);

	let averageRating = $derived(
		feedbacks.length > 0
			? (feedbacks.reduce((acc, f) => acc + f.rating, 0) / feedbacks.length).toFixed(1)
			: 0
	);
</script>

<div class="space-y-8">
	<div class="flex flex-col justify-between gap-4 md:flex-row md:items-center">
		<div>
			<h1 class="mb-2 text-3xl font-bold text-gray-900">User Feedback</h1>
			<p class="text-gray-500">View customer ratings and experiences</p>
		</div>
		<button
			onclick={fetchFeedbacks}
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

	<!-- Satisfaction Metric -->
	<div
		class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 text-white shadow-lg"
	>
		<div class="absolute top-0 right-0 p-8 opacity-10">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="h-32 w-32"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
		</div>
		<div class="relative z-10">
			<p class="mb-2 text-sm font-medium tracking-widest text-blue-100 uppercase">
				Overall Satisfaction
			</p>
			<div class="flex items-baseline space-x-2">
				<span class="text-5xl font-bold">{averageRating}</span>
				<span class="text-2xl text-blue-200">/ 5.0</span>
			</div>
			<p class="mt-4 text-blue-100">Based on {feedbacks.length} user reviews</p>
		</div>
	</div>

	{#if isLoading && feedbacks.length === 0}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each Array(6) as _}
				<div class="h-64 animate-pulse rounded-3xl bg-gray-50"></div>
			{/each}
		</div>
	{:else if error}
		<div class="rounded-2xl border border-red-100 bg-red-50 py-20 text-center">
			<p class="mb-4 font-medium text-red-600">{error}</p>
			<button onclick={fetchFeedbacks} class="font-bold text-red-700 hover:underline"
				>Try Again</button
			>
		</div>
	{:else if feedbacks.length === 0}
		<div class="rounded-3xl border border-gray-100 bg-white py-20 text-center text-gray-400">
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
					d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
				/>
			</svg>
			<p class="text-xl font-medium">No feedback received yet</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each feedbacks as feedback, i}
				<div in:fly={{ y: 20, duration: 300, delay: i * 50 }}>
					<FeedbackCard {feedback} />
				</div>
			{/each}
		</div>
	{/if}
</div>
