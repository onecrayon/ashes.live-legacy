<template>
	<ul class="listing">
		<no-results></no-results>
		<li v-for="card of listing" :key="card.id" class="card-detail">
			<div class="thumbnail">
				<i class="fa fa-4x" :class="typeToFontAwesome(card.type)" aria-hidden="true"></i>
				<img :src="assetPath(card.images.thumbnail)" :alt="card.name">
				<qty-buttons v-if="!isCardGallery" :card="card"></qty-buttons>
			</div>
			<div class="details" :class="{'with-statline': hasStatline(card)} ">
				<h3>
					<card-link :card="card"></card-link>
					<span v-if="card.phoenixborn" class="phoenixborn" :title="card.phoenixborn">
						({{ card.phoenixborn.split(' ')[0] }})
					</span>
				</h3>
				<p class="meta">{{ card.type }} <span class="divider"></span> {{ card.placement }}</p>
				<card-effects :card="card"></card-effects>
				<ul v-if="hasStatline(card)" class="statline">
					<li v-if="card.attack !== undefined" class="attack">Attack {{ card.attack }}</li>
					<li v-if="card.life !== undefined" class="life">Life {{ card.life }}</li>
					<li v-if="card.recover !== undefined" class="recover">Recover {{ card.recover }}</li>
				</ul>
			</div>
			<ol class="costs">
				<li v-for="cost of card.cost" class="cost">
					<span v-if="isArray(cost)" class="parallel-costs">
						<span v-for="splitCost of cost" class="cost">
							<card-codes :content="splitCost"></card-codes>
						</span>
					</span>
					<card-codes v-else :content="cost"></card-codes>
				</li>
			</ol>
		</li>
	</ul>
</template>

<script>
	import {isArray, startsWith} from 'lodash'
	import {assetPath, globals, typeToFontAwesome} from 'app/utils'
	import CardCodes from 'app/components/card_codes.vue'
	import CardLink from 'app/components/card_link.vue'
	import CardEffects from './card_effects.vue'
	import NoResults from './no_results.vue'
	import QtyButtons from './qty_buttons.vue'
	
	export default {
		components: {
			'card-effects': CardEffects,
			'card-link': CardLink,
			'no-results': NoResults,
			'qty-buttons': QtyButtons,
			'card-codes': CardCodes
		},
		computed: {
			listing () {
				return this.$store.state.listing
			},
			isCardGallery () {
				return globals.galleryOnly
			}
		},
		methods: {
			isArray,
			startsWith,
			assetPath,
			typeToFontAwesome,
			hasStatline (card) {
				return card.attack !== undefined ||
					card.life !== undefined ||
					card.recover !== undefined
			}
		}
	}
</script>
