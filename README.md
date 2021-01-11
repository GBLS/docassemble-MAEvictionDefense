# docassemble.MAEvictionDefense

A guided interview for pro se eviction defense in Massachusetts, using the project
name MADE, Massachusetts Defense for Eviction. Generates an Answer form, 
Request for Discovery, and accompanying forms and motions.

## Changelog

* 2021-01-05 Bug fix when using new attorney name
* 2021-01-04 Add support for attorney entering appearance
* 2021-01-03 Integrate language files
* 2020-12-10 Edit additional tenant signature
* 2020-12-02 Language tweaks, compatibility with docassemble 1.2.7
* 2020-11-18 Translate section labels
* 2020-11-17 Integrate feedback from housing coalition
* 2020-11-14 New feedback form that creates Github issues
* 2020-11-13 Added CARES/CDC language to Answer
* 2020-11-09 Update language to reflect Housing Court standing order 6-20
* 2020-10-14 Integrate Tyler videos
* 2020-09-18 Improved Spanish translation/added Spanish videos
* 2020-08-18 Incorporate non-essential eviction defenses/discovery
* 2020-08-10 Make save/load answers easier to see; highlight sign-in link
* 2020-07-28 Update gbls_intake.py to account for breaking change upstream
* 2020-07-27 Added Covid-19 language
* 2020-03-16 Fix incorrect indentation in text reminder
* 2020-03-02 Explicitly list Boston neighborhoods for GBLS intake
* 2020-02-20 Added first draft of optional additional defendants
* 2020-02-18 Tweaks to intake case preview
* 2020-01-20 No longer show "Anonymous User" if someone is not logged in
* 2020-01-07 Better intake (require contact info), updated Spanish translation
* 2019-12-17 Improved signature page
* 2019-12-04 Additional efforts to reduce resource exhaustion. Add intake to GBLS's Legal Server instance
* 2019-11-27 stagger survey emails; other cron randomization to reduce risk of resource exhaustion
* 2019-11-25 Added survey link; fix Monday holiday problem; language fixes
* 2019-08-12 Fixed bug with MRVP
* 2019-08-09 Language fixes
* 2019-08-07 Language fixes
* 2019-08-02 Language fixes
* 2019-07-12 Language fixes
* 2019-06-26 Added 4 new languages: Vietnamese, Haitian Creole, Chinese (Traditional) and Portuguese
* 2019-06-04 Language translation prep
* 2019-05-28 Added question IDs
* 2019-05-01 Improved instructions for discovery requests
* 2019-03-25 Cleaned up instructions, bugfixes
* Bugfix - ls_email
* Test
* 2019-02-18 Bugfixes (transition to new MACourt object)
* 2019-02-14 Bugfixes
* 2019-02-14 Resolve bugs in Spanish language version (unicode errors)
* 2019-02-12 Fix survey link
* 2019-02-11 Layout improvements for initial screen; bugfixes  
* 2019-02-11 Migrate to object-based MACourts module with complete court list
* 2019-02-01 Bugfixes
* 2019-01-20 Language improvements from court
* 2019-01-16 Bugfixes
* 2019-01-11 Error with late answer date calculation
* 2018-12-27 First version with complete Spanish language translation
* 2018-12-26 Bug fixes. Added survey email
* 2018-12-19 Bug fixes / language improvements suggested by court staff
* 2018-12-16 urgent bug fix with illegal characters in download filename
* 2018-12-15 Improved language, handle compel discovery form better if user is not going to return to online interview
* 2018-12-13 Added clinic feature, slight language cleanup and require date_received_ntq if it is known
* 2018-12-10 Fix bug w/ landlord's attorney's name
* 2018-12-04 Many improvements to language and workflow suggested by attorney/advocate feedback. New interpreter notice
* 2018-11-06 Added sharing menu link, support signing on phones
* 2018-11-04 Remove Evacuation Day -- not observed by courts
* 2018-11-03 Account for holidays. New cover sheet designed by Rina
* 2018-11-01 Fixed regression: restored SMS messaging, bug on nonpayment of rent cure
* 2018-10-29 Began groundwork for Spanish translation; bugfixes and major reorganization
* 2018-10-24 Bugfix (additional fields required but hidden)
* 2018-10-24 Bugfix (foreclosure field required). Groundwork for separate motion to compel
* 2018-10-19 Worked on interview flow and hid more irrelevant questions
* 2018-10-18 Added condo conversion defense. Enhanced discovery. Language and review screen cleanup
* 2018-10-11 Added experimental support for reviewing and editing answers (~ 80% coverage)
* 2018-10-04 / 2018-10-05 Bug fixes-security deposit, replace URLs so not blocked by SMS spam measures
* 2018-08-18 Explain discovery to pro se users, review initial defenses, add detail to answer
* 2018-08-17 Email reminders, compact attachments page and wording / help improvements
* 2018-07-08 Bug fixes
* 2018-07-01 Added videos created by MLRI

## Contributors:
    
1. Quinten Steenhuis, Esq. ([Greater Boston Legal Services](https://www.gbls.org))
1. Rina Padua ([Greater Boston Legal Services](https://www.gbls.org) and Harvard University [Phillips Brooks House](http://pbha.org/))
1. Caroline Robinson ([Massachusetts Law Reform Institute](http://www.mlri.org))
1. Mariah Jennings-Rampsi, Esq. ([Volunteer Lawyer's Project](https://www.vlpnet.org/))
