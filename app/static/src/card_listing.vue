<template>
	<ul class="listing">
		<li v-for="card of listing" :key="card.id" class="card-detail">
			<div class="thumbnail">
				<img :src="card.images.thumbnail" :alt="card.name">
				<div class="btn-group">
					<button class="btn btn-qty"
						:class="{active: isQtyActive(card.id, 0)}">0</button
					><button class="btn btn-qty"
						:class="{active: isQtyActive(card.id, 1)}">1</button
					><button class="btn btn-qty"
						:class="{active: isQtyActive(card.id, 2)}">2</button
					><button class="btn btn-qty"
						:class="{active: isQtyActive(card.id, 3)}">3</button>
				</div>
			</div>
			<div class="details" :class="{'with-statline': hasStatline(card)} ">
				<h3>
					<a :href="cardUrl(card)" class="card">{{ card.name }}</a>
					<span v-if="card.phoenixborn" class="phoenixborn" :title="card.phoenixborn">
						({{ card.phoenixborn.split(' ')[0] }})
					</span>
				</h3>
				<p class="meta">{{ card.type }} <span class="divider"></span> {{ card.placement }}</p>
				<ol class="effects">
					<li v-for="effect of card.text" :class="[effect.inexhaustible ? 'inexhaustible' : '']">
						<strong v-if="effect.name" :title="effectTextTooltip(effect)">
							{{ effect.name }}</strong
						><span v-if="effect.cost" class="costs"
							><span v-if="effect.name">: </span
						><span v-for="cost of effect.cost" class="cost"
								v-html="parseCardText(cost)"></span></span
						><span v-if="!effect.name || isEffectTextException(effect)"
							><span v-if="effect.name || effect.cost">: </span
						><span v-html="parseCardText(effect.text)"></span></span>
					</li>
				</ol>
				<ul v-if="hasStatline(card)" class="statline">
					<li v-if="card.attack !== undefined" class="attack">Attack {{ card.attack }}</li>
					<li v-if="card.life !== undefined" class="life">Life {{ card.life }}</li>
					<li v-if="card.recover !== undefined" class="recover">Recover {{ card.recover }}</li>
				</ul>
			</div>
			<ol class="costs">
				<li v-for="cost of card.cost" class="cost" v-html="parseCardText(cost)"></li>
			</ol>
		</li>
	</ul>
</template>

<script>
	import {cardUrl, parseCardText} from './utils'
	import {startsWith} from 'lodash'
	
	export default {
		computed: {
			listing () {
				return this.$store.state.listing
			}
		},
		methods: {
			cardUrl,
			parseCardText,
			hasStatline (card) {
				return card.attack !== undefined
					|| card.life !== undefined
					|| card.recover !== undefined
			},
			isQtyActive (id, qty) {
				// TODO: write actual counting logic
				return qty == 0
			},
			isEffectTextException (effect) {
				return startsWith(effect.name, 'Focus') || startsWith(effect.name, 'Respark')
			},
			effectTextTooltip (effect) {
				if (effect.text && !this.isEffectTextException(effect)) {
					return effect.text
				}
			},
			startsWith (str, substr) {
				return startsWith(str, substr)
			}
		}
	}
</script>

