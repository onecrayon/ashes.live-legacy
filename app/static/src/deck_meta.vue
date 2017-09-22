<template>
	<div id="editor-meta">
		<div class="deck-header">
			<div class="input-group">
				<div class="form-field">
					<input v-model="title" :disabled="!phoenixborn" type="text" placeholder="Untitled deck">
				</div>
				<button v-on:click="save" :disabled="!phoenixborn" class="btn btn-primary">Save</button>
			</div>
		</div>
		<div v-if="phoenixborn" class="phoenixborn-detail">
			<h3>
				<i v-on:click="clearPhoenixborn" class="fa fa-refresh" title="Swap Phoenixborn"></i>
				<a :href="cardUrl(phoenixborn)" class="card">{{ phoenixborn.name }}</a>
			</h3>
		</div>
	</div>
</template>

<script>
	import qwest from 'qwest'
	import {cardUrl} from './utils'

	export default {
		computed: {
			title: {
				get () {
					return this.$store.state.deck.title
				},
				set (value) {
					this.$store.commit('setTitle', value)
				}
			},
			phoenixborn () {
				return this.$store.state.deck.phoenixborn
			}
		},
		methods: {
			cardUrl,
			clearPhoenixborn () {
				this.$store.commit('setTypes', ['Phoenixborn'])
				this.$store.commit('setPhoenixborn', null)
				this.$store.commit('filterCards')
			},
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
