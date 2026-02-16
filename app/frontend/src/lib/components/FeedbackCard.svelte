<script lang="ts">
	import type { Feedback } from '$lib/api';

	let { feedback }: { feedback: Feedback } = $props();

	function renderStars(rating: number) {
		return Array(5)
			.fill(0)
			.map((_, i) => i < rating);
	}
</script>

<div
	class="mb-4 flex h-full flex-col rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:shadow-lg"
>
	<div class="mb-4 flex items-start justify-between">
		<div class="flex items-center space-x-4">
			<div
				class="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 text-xl font-bold text-white shadow-md"
			>
				{feedback.user_name.charAt(0).toUpperCase()}
			</div>
			<div>
				<h3 class="mb-1 leading-none font-bold text-gray-900">{feedback.user_name}</h3>
				<span class="text-xs font-medium text-gray-400">User ID: {feedback.user_id}</span>
			</div>
		</div>
		<div class="flex space-x-0.5">
			{#each renderStars(feedback.rating) as isFilled}
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class={`h-5 w-5 ${isFilled ? 'text-yellow-400' : 'text-gray-200'}`}
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<path
						d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
					/>
				</svg>
			{/each}
		</div>
	</div>

	<div class="mb-4 flex-1 rounded-xl border border-gray-100/50 bg-gray-50/50 p-4">
		<p class="leading-relaxed text-gray-700 italic">
			"{feedback.comment || 'No comment provided.'}"
		</p>
	</div>

	<div class="mt-auto flex items-center justify-between border-t border-gray-50 pt-4">
		<span class="text-xs leading-none font-bold tracking-widest text-gray-400 uppercase"
			>Verified Experience</span
		>
		<div class="flex items-center text-gray-400">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="mr-1.5 h-3 w-3"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			<span class="text-xs font-medium">{feedback.comment_time}</span>
		</div>
	</div>
</div>
