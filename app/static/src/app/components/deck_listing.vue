<template>
	<div>
		<h3>
			Cards
			<span class="card-count float-right">
				<span :class="{error: totalCards > 30}">{{ totalCards }}</span> / 30
			</span>
		</h3>
		<div v-for="section of deckSections" :key="section.title" class="deck-section">
			<hr v-if="section.title == 'Conjuration Deck'">
			<h4>{{ section.title }}<span v-if="section.count" class="card-count"> ({{ section.count }})</span></h4>
			<ul>
				<li v-for="card of section.contents" :key="card.data.id">
					<div v-if="section.title == 'Conjuration Deck' || viewOnly">
						{{ card.count }}&times; <card-link :card="card.data"></card-link>
						<span v-if="card.data.phoenixborn && section.title !== 'Conjuration Deck'"
								class="phoenixborn" :title="card.data.phoenixborn">
							({{ card.data.phoenixborn.split(' ')[0] }})
						</span>
					</div>
					<div v-else>
						<qty-buttons :card="card.data" classes="btn-small"
							zero-output="<i class='fa fa-times' title='Remove'></i>"></qty-buttons>
						<card-link :card="card.data"></card-link>
						<span v-if="card.data.phoenixborn" class="phoenixborn" :title="card.data.phoenixborn">
							({{ card.data.phoenixborn.split(' ')[0] }})
						</span>
					</div>
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	import CardLink from 'app/components/card_link.vue'
	import QtyButtons from 'app/gallery/listing/qty_buttons.vue'

	export default {
		props: ['viewOnly'],
		components: {
			'card-link': CardLink,
			'qty-buttons': QtyButtons,
		},
		computed: {
			deckSections () {
				return this.$store.getters.deckSections
			},
			totalCards () {
				return this.$store.getters.totalCards
			},
		}
	}
</script>
