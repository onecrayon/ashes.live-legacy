<template>
	<div id="editor-gallery">
		<div v-if="phoenixborn" class="gallery">
			<div class="filters">
				<p>Filters coming soon...</p>
			</div>
			<ul class="listing">
				<li v-for="card of listing" :key="card.id">
					<img :src="card.images.thumbnail" :alt="card.name">
					<div>
						<h3>{{ card.name }}</h3>
					</div>
				</li>
			</ul>
		</div>
		<div v-else class="phoenixborn-picker">
			<ul class="listing">
				<li v-for="card of listing" :key="card.id">
					<img v-on:click="phoenixborn = card.id" :src="card.images.compressed" :alt="card.name">
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
					this.$store.commit('filterCards')
				}
			},
			listing () {
				return this.$store.state.listing
			}
		}
	}
</script>
