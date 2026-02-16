<script lang="ts">
	import { api } from '$lib/api';
	import { apiKey } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let isLoading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		isLoading = true;

		try {
			const response = await api.login({ username, password });
			if (response.ErrorCode === 0) {
				const data = response.Data as { api_key: string };
				apiKey.set(data.api_key);
				goto('/queries');
			} else {
				error = response.Message || 'Login failed';
			}
		} catch (err) {
			error = 'An error occurred. Please check your connection.';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}
</script>

<div
	class="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 p-6"
>
	<!-- Animated Background Elements -->
	<div
		class="animate-blob absolute top-[-10%] left-[-10%] h-[40%] w-[40%] rounded-full bg-blue-500 opacity-30 mix-blend-multiply blur-3xl filter"
	></div>
	<div
		class="animate-blob animation-delay-2000 absolute right-[-10%] bottom-[-10%] h-[40%] w-[40%] rounded-full bg-purple-500 opacity-30 mix-blend-multiply blur-3xl filter"
	></div>
	<div
		class="animate-blob animation-delay-4000 absolute top-[20%] right-[10%] h-[30%] w-[30%] rounded-full bg-pink-500 opacity-20 mix-blend-multiply blur-3xl filter"
	></div>

	<!-- Login Card -->
	<div class="relative z-10 w-full max-w-md">
		<div class="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-xl">
			<div class="mb-10 text-center">
				<div
					class="mb-6 inline-flex h-20 w-20 items-center justify-center rounded-2xl border border-white/20 bg-white/10 backdrop-blur-md"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-10 w-10 text-white"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 00-2 2zm10-10V7a4 4 0 00-8 0v4h8z"
						/>
					</svg>
				</div>
				<h2 class="mb-2 text-3xl font-bold text-white">Welcome Back</h2>
				<p class="text-blue-100/70">MailFlow Admin Portal</p>
			</div>

			<form onsubmit={handleSubmit} class="space-y-6">
				<div>
					<label for="username" class="mb-2 block text-sm font-medium text-blue-100">Username</label
					>
					<input
						type="text"
						id="username"
						bind:value={username}
						required
						class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-blue-200/30 transition-all focus:bg-white/10 focus:ring-2 focus:ring-blue-500 focus:outline-none"
						placeholder="admin_user"
					/>
				</div>

				<div>
					<label for="password" class="mb-2 block text-sm font-medium text-blue-100">Password</label
					>
					<input
						type="password"
						id="password"
						bind:value={password}
						required
						class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-blue-200/30 transition-all focus:bg-white/10 focus:ring-2 focus:ring-blue-500 focus:outline-none"
						placeholder="••••••••"
					/>
				</div>

				{#if error}
					<div
						class="animate-shake rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200"
					>
						{error}
					</div>
				{/if}

				<button
					type="submit"
					disabled={isLoading}
					class="flex w-full transform items-center justify-center space-x-2 rounded-xl bg-white px-6 py-3 font-bold text-blue-900 transition-all hover:scale-[1.02] hover:bg-blue-50 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
				>
					{#if isLoading}
						<svg
							class="h-5 w-5 animate-spin text-blue-900"
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
						>
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
					<span>{isLoading ? 'Signing In...' : 'Sign In'}</span>
				</button>
			</form>
		</div>
	</div>
</div>

<style>
	@keyframes blob {
		0% {
			transform: translate(0px, 0px) scale(1);
		}
		33% {
			transform: translate(30px, -50px) scale(1.1);
		}
		66% {
			transform: translate(-20px, 20px) scale(0.9);
		}
		100% {
			transform: translate(0px, 0px) scale(1);
		}
	}

	.animate-blob {
		animation: blob 7s infinite;
	}

	.animation-delay-2000 {
		animation-delay: 2s;
	}

	.animation-delay-4000 {
		animation-delay: 4s;
	}

	@keyframes shake {
		0%,
		100% {
			transform: translateX(0);
		}
		25% {
			transform: translateX(-4px);
		}
		75% {
			transform: translateX(4px);
		}
	}

	.animate-shake {
		animation: shake 0.2s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
	}
</style>
