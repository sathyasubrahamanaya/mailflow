<script lang="ts">
	import type { UserQuery } from '$lib/api';
	import { api } from '$lib/api';
	import { slide } from 'svelte/transition';

	let { query, onReply }: { query: UserQuery; onReply: () => void } = $props();

	let isReplying = $state(false);
	let replyText = $state('');
	let isLoading = $state(false);
	let error = $state('');

	const statusColors: Record<string, string> = {
		open: 'bg-green-100 text-green-700 border-green-200',
		closed: 'bg-gray-100 text-gray-700 border-gray-200',
		pending: 'bg-yellow-100 text-yellow-700 border-yellow-200'
	};

	async function submitReply() {
		if (!replyText.trim()) return;
		isLoading = true;
		error = '';

		try {
			const res = await api.replyToQuery(query.id, replyText);
			if (res.ErrorCode === 0) {
				isReplying = false;
				replyText = '';
				onReply();
			} else {
				error = res.Message;
			}
		} catch (err) {
			error = 'Failed to send reply';
		} finally {
			isLoading = false;
		}
	}
</script>

<div
	class="group mb-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:shadow-md"
>
	<div class="mb-4 flex items-start justify-between">
		<div>
			<div class="mb-2 flex items-center space-x-3">
				<span class="text-xs font-bold tracking-wider text-gray-400 uppercase"
					>Query ID: {query.id}</span
				>
				<span
					class={`rounded-full border px-3 py-1 text-xs font-semibold ${statusColors[query.status.toLowerCase()] || statusColors.pending}`}
				>
					{query.status}
				</span>
			</div>
			<div class="flex items-center space-x-2">
				<div
					class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600"
				>
					{query.user_id}
				</div>
				<span class="text-sm font-medium text-gray-600">User #{query.user_id}</span>
			</div>
		</div>
		{#if query.status.toLowerCase() !== 'closed'}
			<button
				onclick={() => (isReplying = !isReplying)}
				class="flex items-center rounded-lg px-4 py-2 text-sm font-semibold text-blue-600 transition-colors hover:bg-blue-50"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="mr-2 h-4 w-4"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
					/>
				</svg>
				{isReplying ? 'Cancel' : 'Reply'}
			</button>
		{/if}
	</div>

	<p class="mb-6 text-lg leading-relaxed text-gray-800">
		{query.query_text}
	</p>

	{#if query.reply}
		<div class="mt-4 rounded-xl border border-blue-100 bg-blue-50/50 p-4">
			<div class="mb-2 flex items-center justify-between">
				<span class="text-xs font-bold tracking-wider text-blue-600 uppercase">Admin Reply</span>
				<span class="text-xs text-gray-400">{query.reply_time}</span>
			</div>
			<p class="text-gray-700 italic">"{query.reply}"</p>
		</div>
	{/if}

	{#if isReplying}
		<div transition:slide class="mt-6 border-t border-gray-100 pt-6">
			<textarea
				bind:value={replyText}
				placeholder="Type your response here..."
				class="h-32 w-full resize-none rounded-xl border border-gray-200 bg-gray-50 p-4 transition-all outline-none focus:bg-white focus:ring-2 focus:ring-blue-500"
			></textarea>

			{#if error}
				<p class="mt-2 text-sm text-red-500">{error}</p>
			{/if}

			<div class="mt-4 flex justify-end">
				<button
					onclick={submitReply}
					disabled={isLoading || !replyText.trim()}
					class="flex items-center rounded-xl bg-blue-600 px-6 py-2 font-bold text-white transition-all hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
				>
					{#if isLoading}
						<svg class="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24">
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
					{/if}
					Send Reply
				</button>
			</div>
		</div>
	{/if}
</div>
