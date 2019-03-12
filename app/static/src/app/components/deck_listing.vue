<template>
	<div>
		<h3 class="responsive-cols no-wrap">
			<div class="col-flex">
				Cards
				<span class="card-count">
					(<span :class="{error: totalCards > 30}">{{ totalCards }}</span> / 30)
				</span>
			</div>
			<span v-if="enableAshes500" class="ashes-500-score col" :class="{error: ashes500Score > 500}">
				<i class="fa fa-tachometer" aria-hidden="true"></i>
				{{ ashes500Score }}
			</span>
		</h3>
		<div v-for="section of deckSections" :key="section.title" class="deck-section">
			<hr v-if="section.isConjurations">
			<h4>{{ section.title }}<span v-if="section.count" class="card-count"> ({{ section.count }})</span></h4>
			<ul>
				<li v-for="card of section.contents" :key="card.data.id">
					<div v-if="section.isConjurations || viewOnly" class="responsive-cols no-wrap">
						<div class="col-flex">
							{{ card.count }}&times; <card-link :card="card.data"></card-link>
							<span v-if="card.data.phoenixborn && !section.isConjurations"
									class="phoenixborn" :title="card.data.phoenixborn">
								({{ card.data.phoenixborn.split(' ')[0] }})
							</span>
						</div>
						<ashes-500-costs v-if="enableAshes500 && card.data.ashes_500_costs" :card="card" class="col"></ashes-500-costs>
					</div>
					<div v-else class="responsive-cols no-wrap">
						<div class="col-flex responsive-cols no-wrap">
							<div class="col">
								<qty-buttons :card="card.data" classes="btn-small"
									zero-output="<i class='fa fa-times' title='Remove'></i>"></qty-buttons>
							</div>
							<div class="col-flex">
								<card-link :card="card.data"></card-link>
								<span v-if="card.data.phoenixborn" class="phoenixborn" :title="card.data.phoenixborn">
									({{ card.data.phoenixborn.split(' ')[0] }})
								</span>
							</div>
						</div>
						<ashes-500-costs v-if="enableAshes500 && card.data.ashes_500_costs" :card="card" class="col"></ashes-500-costs>
						<span v-else-if="enableAshes500" class="error col">
							<i class="fa fa-exclamation-triangle" title="Currently unsupported by Ashes 500"></i>
						</span>
					</div>
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	import CardLink from 'app/components/card_link.vue'
	import Ashes500Costs from 'app/components/ashes_500_costs.vue'
	import QtyButtons from 'app/gallery/listing/qty_buttons.vue'

	export default {
		props: ['viewOnly'],
		components: {
			'card-link': CardLink,
			'qty-buttons': QtyButtons,
			'ashes-500-costs': Ashes500Costs,
		},
		computed: {
			deckSections () {
				return this.$store.getters.deckSections
			},
			totalCards () {
				return this.$store.getters.totalCards
			},
			enableAshes500 () {
				return this.$store.state.options.enableAshes500
			},
			ashes500Score () {
				return this.$store.getters.ashes500Score
			}
		}
	}
</script>
