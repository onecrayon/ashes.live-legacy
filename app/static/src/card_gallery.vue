<template>
	<div id="editor-gallery">
		<div v-if="phoenixborn" class="gallery">
			<div class="filters">
				<p>Filters and card listings coming soon...</p>
			</div>
		</div>
		<div v-else class="phoenixborn-picker">
			<p>Pick a phoenixborn!</p>
		</div>
	</div>
</template>

<script>
	export default {
		computed: {
			phoenixborn () {
				return this.$store.state.deck.phoenixborn
			}
		}
	}
</script>
