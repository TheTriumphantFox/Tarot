# Thorn Reliquary production prompts

All 78 faces were produced with the built-in image generator, one card per
generation. `design-concept.png` established the direction and
`faces/major_02_the_high_priestess.png` was the production style reference for
the remaining individual faces.

## Shared face prompt

```text
Use case: stylized-concept
Asset type: production tarot card face for a local Windows desktop app
Input image: style reference only.
Primary request: Create <CARD> as one complete isolated portrait card in the
Thorn Reliquary Tarot.
Subject and required symbolism: <CARD-SPECIFIC SCENE>.
Style: match the reference exactly: ninth- to eleventh-century Insular and
early Romanesque illuminated manuscript, primitive woodcut pressure,
iron-gall outline, flat symbolic perspective, egg-tempera pigments, and sparse
tarnished gold.
Composition: 2:3 portrait; entire card visible; narrow iron reliquary border,
four corner rivets, braided knotwork, and a top circular rank medallion.
Palette: soot black, smoked umber, old bone, iron gray, oxidized verdigris,
faded madder, muted ochre, and sparse tarnished gold.
Texture: worn vellum, softened corners, hand-oil patina, faint smoke staining,
small pinholes, abraded pigment, and flaking gilding; symbolism stays readable.
Constraints: one straight-on card; no title, caption, extra text, watermark,
photorealism, Renaissance painting, Victorian occult styling, modern fantasy,
glossy finish, nudity, gore, or graphic harm.
```

For Ace through Ten, every prompt also included this invariant:

```text
CRITICAL COUNT RULE: show exactly <RANK> <SUIT OBJECTS> in the central
illustration, no more and no fewer. Every object must be recognizable,
separate, unobscured, and easy to count. Border ornament and the top rank
medallion must not resemble extra suit objects.

NUMBER RULE: numbered Minor Arcana use a single Arabic numeral in the top
medallion. Roman numerals are reserved for Major Arcana.
```

## Major Arcana scene set

- 0 The Fool: barefoot pilgrim leaving a ruined Roman road with a white hound,
  bundle, hawthorn staff, broken milestone, and rising lark.
- I The Magician: monastic craft-worker at a bench with wand, cup, sword, and
  coin, joining a celestial gesture to practical work.
- II The High Priestess: abbess-seer between pale and dark standing stones at
  a sealed well, holding a closed codex and iron key beneath a crescent moon.
- III The Empress: crowned land-mother beneath a fruiting apple tree with
  spindle, grain sheaf, spring, and nursing deer.
- IV The Emperor: hill-fort steward on a stone throne with measuring rod,
  keys, boundary stones, ram, and winter oak.
- V The Hierophant: monastic teacher beneath a carved arch with two novices,
  wax tablets, crossed keys, bell, and reliquary.
- VI The Lovers: two equal travelers exchanging rings before a flowering
  hawthorn where a garden road and difficult hill road divide.
- VII The Chariot: determined traveler guiding a timber chariot drawn by one
  black ox and one white ox along a marsh causeway.
- VIII Strength: healer gently removing a thorn from a lion's paw beneath a
  summer oak and endless knot.
- IX The Hermit: old monk on a snowy path carrying a horn lantern with one
  golden star, watched by a fox.
- X Wheel of Fortune: great mill wheel turning in a flooded monastery yard as
  figures rise and descend through changing seasons.
- XI Justice: woman judge at an open gate with balanced bronze scales, straight
  sword, and witnesses on both sides.
- XII The Hanged Man: a serene pilgrim visibly suspended by one ankle from a
  living tree above a still spring, free leg crossed, halo bright, seeing the
  landscape inverted; the pose is voluntary and non-violent.
- XIII Death: black-cloaked bell keeper crossing a harvested autumn field as
  old tokens are laid down and new green shoots emerge.
- XIV Temperance: winged healer pouring between two hammered vessels while
  standing between a spring and stone among medicinal plants.
- XV The Devil: masked bargain-maker at a ledger while two adults hold loose
  red cords tied to appetites; an open gate and unused key remain visible.
- XVI The Tower: empty proud watchtower split by white lightning, opening its
  false crown to dawn while the village remains safely distant.
- XVII The Star: traveler replenishing spring and soil beneath one great star
  and seven small stars after a storm.
- XVIII The Moon: tidal-marsh path between ruined towers, hound and wolf on
  opposite banks, and a small crayfish beneath a crescent moon.
- XIX The Sun: two children dancing safely in a walled herb garden beneath a
  brilliant sun with open gates and a resting white pony.
- XX Judgement: winged herald sounding a bronze horn while living townspeople
  awaken and step from open stone doorways at dawn.
- XXI The World: dancer within a braided hawthorn wreath at four converging
  roads, accompanied by bird, eagle, ox, and lion.

## Minor Arcana scene set

### Cups

- Ace: one overflowing communion cup above a spring.
- Two: two equals exchange two cups at a bridge.
- Three: three friends each raise one cup in harvest celebration.
- Four: three grounded cups and one offered from a cloud beside a withdrawn
  traveler.
- Five: three overturned and two upright cups beside a mourner and bridge.
- Six: six flower-filled cups shared in a monastery garden.
- Seven: seven cloud-borne cups containing seven distinct visions.
- Eight: eight cups in two rows as a pilgrim leaves under an eclipse.
- Nine: one cup held and eight displayed on a shelf; the original ten-cup
  output was corrected during visual review.
- Ten: ten cups form an arch above a harmonious household.
- Courts: curious novice, courteous mounted messenger, healer-abbess, and
  composed harbor steward, each with one cup.

### Wands

- Ace: one flowering hawthorn staff rising from incense-like cloud.
- Two: two staffs frame a fort keeper planning beyond the walls.
- Three: three planted staffs overlook returning ships.
- Four: four staffs form a village homecoming canopy; the returning traveler
  carries no walking stick, cane, pole, or other wand-like object.
- Five: five apprentices cross five practice staffs in friendly competition;
  the staffs form a loose fan and all ten ends remain visible so each of the
  five is continuously traceable.
- Six: exactly three clearly separated companion staffs on the left, one
  central laurel staff carried by the rider, and exactly two clearly separated
  companion staffs on the right: an unmistakable 3 + 1 + 2 total of six.
  Every other welcoming figure has empty hands, and the scene contains no
  banners, poles, crossbars, cords, branches, or other wand-like objects.
- Seven: one defender's staff above six challengers' staffs.
- Eight: eight staffs fly in parallel over river and messenger road.
- Nine: one watchman's staff before a fence of exactly eight individually
  separated staffs.
- Ten: laborer carries ten clearly separated staffs toward a nearby gate.
- Courts: traveling apprentice, fiery mounted retainer, confident craft
  mistress, and visionary hill-fort leader, each with one hawthorn staff.

### Swords

- Ace: one crowned pattern-welded sword above winter mountains.
- Two: two crossed swords held in guarded balance beside a tidal shore.
- Three: three swords pass through a cracked wooden heart reliquary, with no
  person or injury.
- Four: three wall-mounted swords and one sheathed below a sleeping knight.
- Five: three swords gathered and two left by departing rivals after a contest.
- Six: six sheathed swords fixed safely in a ferry's bow during passage.
- Seven: exactly five individually traceable swords carried away and exactly
  two swords left upright beside empty tents.
- Eight: exactly eight individually traceable swords planted around a loosely
  ribbon-bound woman with an open escape gap.
- Nine: nine swords on a wall hanging above a sleepless figure.
- Ten: exactly ten broken swords on a fallen shield as an unharmed traveler
  meets dawn; all ten hilts and enough of every blade remain separately visible
  to verify the count at card size.
- Courts: vigilant messenger, swift courier, candid widow-judge, and ethical
  law-speaker, each with one ceremonial sword.

### Pentacles

- Ace: one five-petal-star pilgrimage coin offered above an herb garden.
- Two: two coins balanced in an endless ribbon above a changing harbor.
- Three: three carved coins above a mason, abbess, and architect collaborating.
- Four: one coin held, one above, and one beneath each foot of a guarded
  treasurer.
- Five: five glowing coins in a monastery window near two winter travelers.
- Six: five coins displayed on the stone plinth and one coin being handed to a
  recipient, for exactly six coins under a steward's balance scale.
- Seven: seven coin-fruits growing separately on a cultivated vine.
- Eight: eight finished coins displayed in two rows of four by an apprentice.
- Nine: nine separately visible coins among the vines of an independent
  landholder's garden, including one high central coin so the 4+1+4 grouping
  is unmistakable.
- Ten: ten coins form a 1-2-3-4 family tree above three generations.
- Courts: farming apprentice, patient field steward, grounded matriarch, and
  master smith-landholder, each with one pilgrimage coin.

## Card-back prompt

The back uses a rotationally balanced thorn-vine labyrinth, four birds,
braided knotwork, iron rivets, opposed flowers, and a non-figurative eclipse
wheel of alternating crescents and rays. It contains no text, faces, numerals,
or upright-only symbols.
