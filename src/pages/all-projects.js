import Head from "next/head"
import React, { useEffect, useState } from "react";
import { NextSeo } from "next-seo";
import { AnimateSharedLayout } from "framer-motion";
import { Layout } from "../layout/Layout";
import { projects } from "../constants/constants";
import { Section, SectionDivider, PageTitle } from "../styles/GlobalComponents";
import { GridContainer } from "../components/Projects/ProjectsStyles";
import ProjectsFilter from "../components/ProjectsFilter/ProjectsFilter";
import ProjectCard from "../components/Cards/ProjectCard";

const AllProjects = () => {
  const [data, setData] = useState([]);
  const [filterBy, setFilterBy] = useState("All");

  useEffect(() => {
    setData(projects);
  }, []);

  const handleFilter = (type) => {
    switch (type) {
      case "javascript":
        setData([...projects].filter((p) => p.mainType === "javascript"));
        setFilterBy("JavaScript");
        break;

      case "php":
        setData([...projects].filter((p) => p.mainType === "php"));
        setFilterBy("PHP");
        break;

      case "react":
        setData([...projects].filter((p) => p.mainType === "react"));
        setFilterBy("React");
        break;

      default:
        setData([...projects]);
        setFilterBy("All");
        break;
    }
  };

  return (
    <>
      <Head>
        <title>All Projects | Muhammed Humam Hossain</title>
      </Head>
    
      <Layout>
        <Section nopadding id="projects">
          <NextSeo
            title="Novatchii Vasile's Projects"
            description="Check out Novatchii Vasile's projects"
            openGraph={{
              description: "Check out Novatchii Vasile's projects",
            }}
          />

          <SectionDivider divider style={{ marginBottom: 0 }} />
          <PageTitle>All My Relevant Projects</PageTitle>
          <ProjectsFilter filter={handleFilter} filterBy={filterBy} />
          <AnimateSharedLayout>
            <GridContainer layout>
              {data
                .sort((a, b) => a.order - b.order)
                .map((card) => (
                  <ProjectCard item={card} key={card.id} />
                ))}
            </GridContainer>
          </AnimateSharedLayout>
        </Section>
      </Layout>
    </>
  );
};

export default AllProjects;
