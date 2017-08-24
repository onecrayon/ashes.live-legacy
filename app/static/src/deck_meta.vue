<template>
	<div id="editor-meta">
		<p>Deck meta WIP: <button v-on:click="incrementCount">+1</button></p>
	</div>
</template>

<script>
	export default {
		methods: {
			incrementCount () {
				this.$store.commit('increment')
			}
		}
	}
</script>
