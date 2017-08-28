<template>
	<div id="editor-meta">
		<div class="deck-header">
			<div class="form-field">
				<input v-model="title" type="text" placeholder="Untitled deck">
			</div>
			<button v-on:click="save" class="btn btn-primary">Save</button>
		</div>
		<div class="phoenixborn-detail">
			<p>Phoenixborn image and deck details forthcoming...</p>
		</div>
	</div>
</template>

<script>
	import qwest from 'qwest'

	export default {
		computed: {
			title: {
				get () {
					return this.$store.state.deck.title
				},
				set (value) {
					this.$store.commit('setTitle', value)
				}
			}
		},
		methods: {
			save () {
				// TODO
				var title = this.$store.state.deck.title
				console.log('Saving? ' + title)
				qwest.get('/api').then(function(xhr, response) {
					console.log('"Saved" deck (' + title + ') with API version: ' + response.version)
				}).catch(function(error, xhr, response) {
					console.log('Failed to save deck: ' + JSON.stringify(response))
				})
			}
		}
	}
</script>
