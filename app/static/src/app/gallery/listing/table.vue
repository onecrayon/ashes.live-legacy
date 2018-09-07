<template>
	<table class="tabular-listing" cellspacing="0" cellpadding="0">
		<tbody>
			<tr v-if="!listing.length && !isDisabled">
				<td :colspan="numColumns" class="no-results">
					<h2>No cards found</h2>
					<p><button @click="resetFilters" class="btn btn-primary">Clear filters</button></p>
				</td>
			</tr>
			<tr v-else-if="!listing.length">
				<td :colspan="numColumns" class="loading-results">
					<p class="callout muted"><i class="fa fa-spinner fa-spin" aria-hidden="true"></i> Loading cards...</p>
				</td>
			</tr>
			<tr v-for="card of listing" :key="card.id">
				<td v-if="isDeckbuilder" class="qty-col">
					<qty-buttons :card="card" classes="btn-small"></qty-buttons>
				</td>
				<td class="type-col" :title="card.type"><i class="fa" :class="typeToFontAwesome(card.type)" aria-hidden="true"></i></td>
				<td class="name-col">
					<card-link :card="card"></card-link>
					<span v-if="card.phoenixborn" class="phoenixborn" :title="card.phoenixborn">
						({{ card.phoenixborn.split(' ')[0] }})
					</span>
					<ashes-500-costs v-if="isAshes500Enabled" :card="card" class="block-level"></ashes-500-costs>
				</td>
				<td class="stats-col">
					<span v-if="hasStatline(card)" class="muted">
						<span v-if="card.attack !== undefined || card.battlefield !== undefined"
							class="attack">{{ card.battlefield || card.attack }}</span>
						<span v-else>&ndash;</span> /
						<span v-if="card.life !== undefined" class="life">{{ card.life }}</span>
						<span v-else>&ndash;</span> /
						<span v-if="card.recover !== undefined || card.spellboard !== undefined"
							class="recover">{{ card.spellboard || card.recover }}</span>
						<span v-else>&ndash;</span>
					</span>
					<card-link v-else-if="card.conjurations" v-for="conjuration of conjurationChain(card.conjurations)" :key="conjuration.id" :card="conjuration">
						<i class="fa" :class="typeToFontAwesome('summon')"></i>
					</card-link>
				</td>
				<td class="costs-col">
					<ol v-if="card.cost" class="costs">
						<li v-for="cost of card.cost" class="cost">
							<span v-if="isArray(cost)" class="parallel-costs">
								<span v-for="splitCost of cost" class="cost">
									<card-codes :content="splitCost"></card-codes>
								</span>
							</span>
							<card-codes v-else :content="cost"></card-codes>
						</li>
					</ol>
					<span v-else class="muted">--</span>
				</td>
			</tr>
		</tbody>
	</table>
</template>

<script>
	import {assign, isArray, startsWith} from 'lodash'
	import {globals, typeToFontAwesome} from 'app/utils'
	import CardCodes from 'app/components/card_codes.vue'
	import CardLink from 'app/components/card_link.vue'
	import Ashes500Costs from 'app/components/ashes_500_costs.vue'
	import QtyButtons from './qty_buttons.vue'
	
	export default {
		components: {
			'card-link': CardLink,
			'qty-buttons': QtyButtons,
			'card-codes': CardCodes,
			'ashes-500-costs': Ashes500Costs,
		},
		computed: {
			isDisabled () {
				return this.$store.state.isDisabled
			},
			listing () {
				return this.$store.state.listing
			},
			numColumns () {
				return globals.galleryOnly ? 4 : 5
			},
			isAshes500Enabled () {
				return this.$store.state.options.enableAshes500
			},
			isDeckbuilder () {
				return !globals.galleryOnly
			}
		},
		methods: {
			isArray,
			startsWith,
			typeToFontAwesome,
			hasStatline (card) {
				return card.attack !== undefined ||
					card.life !== undefined ||
					card.recover !== undefined
			},
			resetFilters () {
				this.$store.commit('resetFilters')
				this.$store.dispatch('filterCards')
			},
			conjurationChain (conjurations, returnMapping) {
				let conjurationMap = {}
				let order = []
				for (const conjuration of conjurations) {
					order.push(conjuration.id)
					conjurationMap[conjuration.id] = conjuration
					if (conjuration.conjurations && conjuration.conjurations.length) {
						const nested = this.conjurationChain(conjuration.conjurations, true)
						order = order.concat(nested.order)
						assign(conjurationMap, nested.map)
					}
				}
				if (returnMapping) {
					return {'order': order, 'map': conjurationMap}
				}
				order = Array.from(new Set(order))
				let cards = []
				for (const cardId of order) {
					cards.push(conjurationMap[cardId])
				}
				return cards
			}
		}
	}
</script>
