<template>
	<div class="tutor-select">
		<i class="fa fa-hand-o-right"></i> 
		<select v-model.number="tutorTarget"
			:disabled="!tutorTargets(card.stub).length">
			<option v-if="tutorTargets(card.stub).length" value="0">Choose card...</option>
			<option v-else value="0">No valid cards</option>
			<optgroup v-for="tutorSection of tutorTargets(card.stub)"
				:key="tutorSection.title" :label="tutorSection.title">
				<option v-for="tutorTarget of tutorSection.contents"
					:key="tutorTarget.data.id"
					:value="tutorTarget.data.id">
					{{ tutorTarget.data.name }}
				</option>
			</optgroup>
		</select>
	</div>
</template>

<script>
	import {assign, filter, includes, isInteger, isString, reduce} from 'lodash'
	import {tutorCards} from 'app/utils'
	import {getPlayCost} from 'app/utils/costs'

	export default {
		props: ['card'],
		computed: {
			tutorTarget: {
				get: function () {
					return this.$store.getters.tutorSelections[this.card.id] || 0
				},
				set: function (value) {
					this.$store.commit('setTutorTarget', {
						'tutorId': this.card.id,
						'targetId': value || null
					})
				}
			}
		},
		methods: {
			tutorTargets (cardStub) {
				const sections = []
				let isValidTarget = function () { return true }
				if (isInteger(tutorCards[cardStub])) {
					isValidTarget = function (cardData) {
						if (!cardData.magicCost) return false
						return tutorCards[cardStub] === getPlayCost(cardData.magicCost)
					}
				} else if (isString(tutorCards[cardStub])) {
					isValidTarget = function (cardData) {
						return tutorCards[cardStub] === cardData.type
					}
				}
				for (const section of this.$store.getters.deckSections) {
					if (section.isConjurations) continue
					const contents = filter(section.contents, (card) => {
						const inUse = reduce(this.$store.getters.tutorTargets, (total, current) => {
							if (current === card.data.id) return total + 1
							return total
						}, 0) + (includes(this.$store.state.deck.first_five, card.data.id) ? 1 : 0)
						if (card.count <= inUse && this.tutorTarget !== card.data.id) {
							return false
						}
						return isValidTarget(card.data)
					})
					if (contents.length) {
						sections.push(assign({}, section, {'contents': contents}))
					}
				}
				return sections
			}
		}
	}
</script>

