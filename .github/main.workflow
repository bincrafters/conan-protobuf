workflow "New workflow" {
  on = "push"
  resolves = ["GitHub Action for Docker"]
}

action "GitHub Action for Docker" {
  uses = "travis-ci/actions@master"
  secrets = ["TRAVIS_TOKEN"]
}
