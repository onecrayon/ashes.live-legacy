<template>
	<div id="editor-gallery">
		<div v-if="phoenixborn" class="gallery">
			<div class="filters">
				<p>Filters and card listings coming soon...</p>
			</div>
		</div>
		<div v-else class="phoenixborn-picker">
			<ul class="listing">
				<li v-for="card of listing" :key="card.id">
					<img v-on:click="phoenixborn = card.id" :src="'/images/cards/' + card.stub + '.jpg'" :alt="card.name">
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	export default {
		created () {
			if (this.$store.state.deck.phoenixborn) {
				this.$store.commit('filterCards')
			} else {
				this.$store.commit('filterCards', {types: ['Phoenixborn']})
			}
		},
		computed: {
			phoenixborn: {
				get () {
					return this.$store.state.deck.phoenixborn
				},
				set (cardId) {
					this.$store.commit('setPhoenixborn', cardId)
				}
			},
			listing () {
				return this.$store.state.listing
			}
		}
	}
</script>
