<template>
	<div id="editor-gallery">
		<div v-if="phoenixborn" class="gallery">
			<div class="filters">
				<div class="btn-group">
					<button v-on:click="toggleDiceLogic"
						class="btn btn-all" :class="{active: diceLogicActive }">{{ diceLogicText }}:</button
					><button v-on:click="toggleDie('ceremonial')"
						class="btn phg-ceremonial-power" :class="{active: ceremonialActive }"
						title="Ceremonial"></button
					><button v-on:click="toggleDie('charm')"
						class="btn phg-charm-power" :class="{active: charmActive }"
						title="Charm"></button
					><button v-on:click="toggleDie('illusion')"
						class="btn phg-illusion-power" :class="{active: illusionActive }"
						title="Illusion"></button
					><button v-on:click="toggleDie('natural')"
						class="btn phg-natural-power" :class="{active: naturalActive }"
						title="Natural"></button
					><button v-on:click="toggleDie('divine')"
						class="btn phg-divine-power" :class="{active: divineActive }" :disabled="set5Disabled"
						title="Divine">D</button
					><button v-on:click="toggleDie('sympathy')"
						class="btn phg-sympathy-power" :class="{active: sympathyActive }" :disabled="set6Disabled"
						title="Sympathy">S</button>
				</div>
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
	import {includes} from 'lodash'
	
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
			},
			diceLogicText () {
				return this.$store.state.filters.diceLogic == 'or' ? 'Any' : 'All'
			},
			diceLogicActive () { return this.$store.state.filters.diceLogic == 'and' },
			ceremonialActive () { return includes(this.$store.state.filters.dice || [], 'ceremonial') },
			charmActive () { return includes(this.$store.state.filters.dice || [], 'charm') },
			illusionActive () { return includes(this.$store.state.filters.dice || [], 'illusion') },
			naturalActive () { return includes(this.$store.state.filters.dice || [], 'natural') },
			divineActive () { return includes(this.$store.state.filters.dice || [], 'divine') },
			sympathyActive () { return includes(this.$store.state.filters.dice || [], 'sympathy') },
			set5Disabled () { return !includes(this.$store.state.filters.releases, 5) },
			set6Disabled () { return !includes(this.$store.state.filters.releases, 6) }
		},
		methods: {
			toggleDiceLogic () {
				this.$store.commit('toggleDiceLogic')
				this.$store.commit('filterCards')
			},
			toggleDie (die) {
				this.$store.commit('toggleDieFilter', die)
				this.$store.commit('filterCards')
			}
		}
	}
</script>
