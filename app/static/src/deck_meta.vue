<template>
	<div id="editor-meta">
		<div class="deck-header">
			<div class="form-field">
				<input v-model="title" type="text" placeholder="Untitled deck">
			</div>
			<button v-on:click="saveDeck" class="btn btn-primary">Save</button>
		</div>
		<div class="phoenixborn-detail">
			<p>Phoenixborn image and deck details forthcoming...</p>
		</div>
	</div>
</template>

<script>
	export default {
		computed: {
			title: {
				get () {
					return this.$store.state.deck.title
				},
				set (value) {
					this.$store.commit('title', value)
				}
			}
		},
		methods: {
			saveDeck () {
				// TODO
				alert('Saving deck `' + this.$store.state.deck.title + '`')
			}
		}
	}
</script>
